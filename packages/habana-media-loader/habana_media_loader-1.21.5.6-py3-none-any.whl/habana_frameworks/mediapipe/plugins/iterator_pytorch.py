import torch
import habana_frameworks.torch.utils.experimental as htexp
import habana_frameworks
import habana_frameworks.torch.hpu as hpu
from habana_frameworks.torch import media_pyt_bridge as mpytpx
from habana_frameworks.mediapipe.backend.iterator import _MediaIterator
from habana_frameworks.mediapipe.media_proxy import HPUProxy
from habana_frameworks.mediapipe.media_types import dtype as dt
import media_pipe_proxy as mppy
from media_pipe_types import dType as mdt

import time
import os
from ctypes import *


# dictionary to convert media data type to torch data type.
media_to_torch_dtype = {mdt.INT8: torch.int8,
                        mdt.UINT8: torch.uint8,
                        mdt.INT16: torch.int16,
                        mdt.UINT16: torch.int16,
                        mdt.FLOAT32: torch.float32,
                        mdt.INT32: torch.int32,
                        mdt.UINT32: torch.int32,
                        mdt.INT64: torch.int64,
                        mdt.UINT64: torch.int64,
                        mdt.BFLOAT16: torch.bfloat16
                        }


class HPUDevice:
    """
    Class defining hpu device.

    """

    def __init__(self, device, device_id):
        """
        Constructor method.

        :params device: device on which mediapipe is to be run. <hpu>
        :params device_id: device id.
        """
        if device != 'hpu':
            raise RuntimeError("device {} not supported!".format(device))

        self.device_id = device_id
        # self.name = 'Gaudi2'

    def release_device(self, device_id):
        """
        Method to release device.

        :params device_id: device id to release.
        """
        if self.device_id != device_id:
            assert False, "Error: Invalid device_id {} for release_device".format(
                self.device_id)

    def get_device_id(self):
        """
        Method to get device ID.

        :returns : device id.
        """
        return self.device_id

    # def __del__(self):
    #    print("HPUDevice destructor")


class PytorchDevice(HPUProxy):
    """
    Class specific to pytorch framework, derived from HPU Proxy.
    This provides functionality to get device id and allocate tensors

    """
    instance = None
    instanceCount = 0

    def __init__(self, name='hpu', device_id=None):
        """
        Constructor method.

        :params name: device on which mediapipe is to be run. <hpu>
        :params device_id: device id.
        """
        if PytorchDevice.instance is None:
            PytorchDevice.instance = HPUDevice(name, device_id)

        PytorchDevice.instanceCount += 1
        self.device = PytorchDevice.instance
        self.torch_device = torch.device(name)
        self.buff_dict = {}
        self.tensor_dict = {}  # TODO: May need to change to list for perf

    def __del__(self):
        """
        Destructor method.

        """
        PytorchDevice.instanceCount -= 1
        if PytorchDevice.instanceCount == 0:
            del PytorchDevice.instance
            PytorchDevice.instance = None

    def new_buffer(self, size):
        """
        Method for creating new buffer.

        :params size: Buffer size in bytes.
        :returns : device address of buffer.
        """
        # TODO: check torch.zeros
        tensor = torch.empty(
            tuple([size]), device=self.torch_device, dtype=torch.uint8)
        t_addr = htexp._data_ptr(tensor)
        self.buff_dict[t_addr] = tensor
        return t_addr

    # def get_data_ptr(self, tensor):
    #    return htexp._data_ptr(tensor)

    def get_compute_stream(self):
        """
        Method to get device compute stream.

        :returns : device compute stream.
        """
        compute = htexp._compute_stream()
        return compute
        # return 0  #TODO: check if not to share Compute Stream

    def new_tensor_dataptr(self, shape, dtype):
        """
        Method to get device tensor.

        :params shape: shape of tensor.
        :params dtype: datatype of tensor.
        :returns : device address of tensor.
        """
        tensor = torch.empty(
            tuple(shape), device=self.torch_device, dtype=media_to_torch_dtype[dtype])
        t_addr = htexp._data_ptr(tensor)
        self.tensor_dict[t_addr] = tensor
        return t_addr

    def get_tensor(self, data_ptr):
        """
        Method to get tensor from device address

        :params data_ptr: return tensor for device address
        """
        return self.tensor_dict[data_ptr]

    def delete_tensor(self, data_ptr):
        """
        Method to free allocated tensor.

        :params data_ptr: device address for which tensor is to be freed.
        """
        del self.tensor_dict[data_ptr]
        # print("pytorch delete_tensor len is ", len(self.tensor_dict), data_ptr)

    def delete_buffer(self, data_ptr):
        """
        Method for freeing buffer.

        :params data_ptr: device address to be freed.
        """
        del self.buff_dict[data_ptr]

    def flush_tensors(self, tensor_l):
        """
        Method to flush pending tensors in queue.

        :params tensor_l: list of device address for which tensors are to be flushed
        """
        # print("flush tensor ", tensor_l," pending list", self.tensor_dict.keys())
        for buffer in tensor_l:
            self.delete_tensor(buffer)

    def get_device_id(self, device_type):  # DeviceType is unused
        """
        Method to get device ID.

        :params device_type: device type. This is unused param.
        :returns : device id.
        """
        # print("pytorch get_device_id devicetype ", device_type)
        return self.device.get_device_id()

    def release_device_id(self, synDeviceId):
        """
        Method to release device.

        :params synDeviceId: device id to release.
        """
        self.device.release_device(synDeviceId)


class MediaGenericPytorchIterator(_MediaIterator):
    """
    Class defining mediapipe iterator for Pytorch framework.
    This class provides functionality to get output tensors from mediapipe.

    """

    proxy_device = None

    def __init__(self, mediapipe, device="mixed", fw_type="NA_FW"):
        """
        Constructor method.

        :params mediapipe: mediapipe
        """
        self.proxy_device = None
        if (device == "cpu"):
            pass
        elif (device == "hpu" or device == "mixed"):
            hpu.init()
            device_id = mediapipe.getDeviceId()
            self.__setup_fw(mediapipe, device_id, fw_type)
        else:
            raise ValueError(f"Invalid device {output_device}")

        mpytpx.RegisterMediaDeleter(mediapipe.close)
        mediapipe.build()

        self.post_proc_func = None

        super().__init__(_pipeline=mediapipe)

    def __setup_fw(self, mediapipe, device_id, fw_type):
        if (fw_type == "PYTHON_FW"):
            if MediaGenericPytorchIterator.proxy_device is None:
                MediaGenericPytorchIterator.proxy_device = PytorchDevice(
                    name='hpu', device_id=device_id)
            self.proxy_device = MediaGenericPytorchIterator.proxy_device

            # os.environ["DISABLE_PP_REALLOC"] = "1"  # only needed for video decode,
            # PP buffers cannot be realloc
            mediapipe.set_proxy(mppy.fwType.PYTHON_FW,
                                MediaGenericPytorchIterator.proxy_device)
            self.get_pyt_tensor = MediaGenericPytorchIterator.proxy_device.get_tensor
        elif (fw_type == "PYT_FW"):
            self.proxy_device = mpytpx.CreatePytMediaProxy(device_id)
            mpytpx.RegisterMediaDeleter(mediapipe.close)
            mediapipe.set_proxy(mppy.fwType.PYT_FW,
                                self.proxy_device)
            self.get_pyt_tensor = mpytpx.GetOutputTensor
        else:
            raise ValueError(f"invalid fw type {fw_type}")

    def register_post_processing_function(self, post_proc_func):
        self.post_proc_func = post_proc_func

    def __iter__(self):
        """
        Method to initialize mediapipe iterator.

        :returns : iterator for mediapipe
        """
        self.pipe.iter_init()
        return self

    def __next__(self):
        outputs = self.pipe.run()
        outputs = [outputs] if type(outputs) is not list else outputs
        output_tensors = []
        for output in outputs:
            if output.device == "cpu":
                output = torch.from_numpy(output.as_nparray())
            else:
                output = self.get_pyt_tensor(output.dev_addr)
            output_tensors.append(output)

        if self.post_proc_func is not None:
            output_tensors = self.post_proc_func(*output_tensors)
        return output_tensors

    def __del__(self):
        del self.pipe
        del self.proxy_device

class HPUGenericPytorchIterator(MediaGenericPytorchIterator):
    """
    Class defining mediapipe iterator for Pytorch framework.
    This class provides functionality to get output tensors from mediapipe.

    """

    def __init__(self, mediapipe):
        """
        Constructor method.

        :params mediapipe: mediapipe
        """
        super().__init__(mediapipe=mediapipe, device="hpu", fw_type="PYTHON_FW")

class HPUResnetPytorchIterator(MediaGenericPytorchIterator):
    """
    Class defining Resnet mediapipe iterator for Pytorch framework.
    This class provides functionality to get output tensors from mediapipe.

    """

    def __init__(self, mediapipe):
        """
        Constructor method.

        :params mediapipe: mediapipe
        """
        super().__init__(mediapipe=mediapipe, device="hpu", fw_type="PYTHON_FW")

        label_tensor_u32 = int(os.getenv("GRECO_INFERENCE", "0"))
        if (label_tensor_u32 == 0):
            def post_proc_func(images, labels):
                return images, labels.long()

            self.register_post_processing_function(post_proc_func)

class CPUHPUResnetPytorchIterator(MediaGenericPytorchIterator):
    """
    Class defining Resnet mediapipe iterator for Pytorch framework.
    This class provides functionality to get output tensors from mediapipe.

    """

    def __init__(self, mediapipe):
        """
        Constructor method.

        :params mediapipe: mediapipe
        """
        super().__init__(mediapipe=mediapipe, device="hpu", fw_type="PYT_FW")

        label_tensor_u32 = int(os.getenv("GRECO_INFERENCE", "0"))
        if (label_tensor_u32 == 0):
            def post_proc_func(images, labels):
                return images, labels.long()

            self.register_post_processing_function(post_proc_func)


class Resnet3dPytorchIterator(HPUResnetPytorchIterator):
    """
    Class defining Resnet3d mediapipe iterator for Pytorch framework.
    This class provides functionality to get output tensors from mediapipe.

    """

    def __init__(self, mediapipe):
        """
        Constructor method.

        :params mediapipe: mediapipe
        """
        super().__init__(mediapipe=mediapipe)


class NextGptPytorchIterator(MediaGenericPytorchIterator):
    """
    Class defining NextGPT mediapipe iterator for Pytorch framework.
    This class provides functionality to get output tensors from mediapipe.

    """

    def __init__(self, mediapipe):
        """
        Constructor method.

        :params mediapipe: mediapipe
        """
        super().__init__(mediapipe=mediapipe, device="hpu", fw_type="PYTHON_FW")
        def post_proc_func(images):
            return images

        self.register_post_processing_function(post_proc_func)


class HPUSsdPytorchIterator(MediaGenericPytorchIterator):
    """
    Class defining SSD mediapipe iterator for Pytorch framework.
    This class provides functionality to get output tensors from mediapipe.

    """

    def __init__(self, mediapipe):
        """
        Constructor method.

        :params mediapipe: mediapipe
        """
        super().__init__(mediapipe=mediapipe)

    def __next__(self):
        """
        Method to run mediapipe iterator over one batch of dataset and return the output tensors.

        :returns : output tensors.
        """
        # lengths is not returned from iterator
        images, ids, sizes, boxes, labels, lengths, batch = self.pipe.run()

        images_tensor = self.proxy_device.get_tensor(images.dev_addr)
        ids_tensor = self.proxy_device.get_tensor(ids.dev_addr)
        sizes_tensor = self.proxy_device.get_tensor(sizes.dev_addr)
        img_size = list(torch.hsplit(sizes_tensor, 2))  # Split the tensor
        b_size = self.pipe.getBatchSize()
        img_size[0] = img_size[0].reshape(b_size)
        img_size[1] = img_size[1].reshape(b_size)

        boxes_tensor = self.proxy_device.get_tensor(boxes.dev_addr)
        labels_tensor = self.proxy_device.get_tensor(labels.dev_addr)

        batch_tensor = self.proxy_device.get_tensor(batch.dev_addr)
        # TODO: check if can be avoided
        batch_tensor_cpu = batch_tensor.to('cpu')
        batch_np = batch_tensor_cpu.numpy()
        batch = batch_np[0]

        if batch < b_size:
            images_tensor = torch.narrow(images_tensor, 0, 0, batch)
            ids_tensor = torch.narrow(ids_tensor, 0, 0, batch)
            img_size[0] = torch.narrow(img_size[0], 0, 0, batch)
            img_size[1] = torch.narrow(img_size[1], 0, 0, batch)
            boxes_tensor = torch.narrow(boxes_tensor, 0, 0, batch)
            labels_tensor = torch.narrow(labels_tensor, 0, 0, batch)
        # TODO: check if labels_tensor.long() needed
        return images_tensor, ids_tensor, img_size, boxes_tensor, labels_tensor.long()


class HPUUnetPytorchIterator(MediaGenericPytorchIterator):
    """
    Class defining Unet mediapipe iterator for Pytorch framework.
    This class provides functionality to get output tensors from mediapipe.

    """

    def __init__(self, mediapipe):
        """
        Constructor method.

        :params mediapipe: mediapipe
        """
        self.first_run = True
        mediapipe.set_repeat_count(-1)
        super().__init__(mediapipe=mediapipe)
        self.iter_len = len(self)
        self.iter_loc = 0

    def __iter__(self):
        """
        Constructor method.

        :params mediapipe: mediapipe
        """
        if (self.first_run):
            super().__iter__()
            self.first_run = False
        return self

    def __next__(self):
        """
        Method to run mediapipe iterator over one batch of dataset and return the output tensors.

        :returns : output tensors.
        """
        if (self.iter_loc < self.iter_len):
            # print("> pipe_run")
            # start_time = time.perf_counter()
            images, labels = self.pipe.run()
            # end_time = time.perf_counter()
            images_tensor = self.proxy_device.get_tensor(images.dev_addr)
            labels_tensor = self.proxy_device.get_tensor(labels.dev_addr)
            # print("< pipe_run take ", end_time-start_time)
            # print("######################################################", flush=True)
            # return images_tensor, labels_tensor
            batch = {}
            batch["image"] = images_tensor
            batch["label"] = labels_tensor
            self.iter_loc += 1
            return batch
        else:
            self.iter_loc = 0
            raise StopIteration


class CPUHPUUnet3DPytorchIterator(MediaGenericPytorchIterator):
    """
    Class defining Unet 3D mediapipe iterator for Pytorch framework.
    This class provides functionality to get output tensors from mediapipe.
    """

    def __init__(self, mediapipe):
        """
        Constructor method.

        :params mediapipe: mediapipe
        """
        super().__init__(mediapipe=mediapipe, device="hpu", fw_type="PYT_FW")

        def post_proc_func(images, labels):
            dict = {}
            dict["image"] = images_tensor
            dict["label"] = labels_tensor
            return dict
        self.register_post_processing_function(post_proc_func)

    def __next__(self):
        """
        Method to run mediapipe iterator over one batch of dataset and return the output tensors.

        :returns : output tensors.
        """
        images, labels = self.pipe.run()
        images_tensor = mpytpx.GetOutputTensor(images.get_addr())
        labels_tensor = mpytpx.GetOutputTensor(labels.get_addr())

        dict = {}
        dict["image"] = images_tensor
        dict["label"] = labels_tensor
        return dict

    def del_iter(self):
        self.pipe.del_iter()


class HPUUnet3DPytorchIterator(MediaGenericPytorchIterator):
    """
    Class defining Unet 3D mediapipe iterator for Pytorch framework.
    This class provides functionality to get output tensors from mediapipe.
    """

    def __init__(self, mediapipe):
        """
        Constructor method.

        :params mediapipe: mediapipe
        """
        super().__init__(mediapipe=mediapipe)

    def __next__(self):
        """
        Method to run mediapipe iterator over one batch of dataset and return the output tensors.

        :returns : output tensors.
        """
        images, labels = self.pipe.run()
        images_tensor = self.proxy_device.get_tensor(images.dev_addr)
        labels_tensor = self.proxy_device.get_tensor(labels.dev_addr)
        dict = {}
        dict["image"] = images_tensor
        dict["label"] = labels_tensor
        return dict

    def del_iter(self):
        pass


class CPUUnetPytorchIterator(MediaGenericPytorchIterator):
    """
    Class defining Unet mediapipe iterator for Pytorch framework.
    This class provides functionality to get output tensors from mediapipe.
    """

    def __init__(self, mediapipe):
        """
        Constructor method.

        :params mediapipe: mediapipe
        """
        self.first_run = True
        super().__init__(mediapipe=mediapipe, device="cpu")

        def post_proc_func(images, labels):
            batch = {}
            batch["image"] = images
            batch["label"] = labels
            return batch
        self.register_post_processing_function(post_proc_func)


class CPUUnet3DPytorchIterator(MediaGenericPytorchIterator):
    def __init__(self, mediapipe):
        """
        Constructor method.

        :params mediapipe: mediapipe
        """
        super().__init__(mediapipe=mediapipe, device="cpu")

        def post_proc_func(images, labels):
            batch = {}
            batch["image"] = images
            batch["label"] = labels
            return batch
        self.register_post_processing_function(post_proc_func)
