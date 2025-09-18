import numpy as np
import time
import math
from habana_frameworks.mediapipe.operators.cpu_nodes.cpu_nodes import media_function
from habana_frameworks.mediapipe import fn  # NOQA
from habana_frameworks.mediapipe.mediapipe import MediaPipe  # NOQA
from habana_frameworks.mediapipe.media_types import dtype as dt  # NOQA

# augmentation probability
g_rand_aug_prob = 0.15

# zoom
g_crop_min = 0.7
g_crop_max = 1.0

# flip
flip_prob = 0.33

# noise
g_min_std_dev = 0.0
g_max_std_dev = 0.33

# gaussian blur
g_max_sigma = 1.5
g_min_sigma = 0.5

# brightness
g_brt_factor_min = 0.7
g_brt_factor_max = 1.3

# contrast
g_scale_min = 0.65
g_scale_max = 1.5


def get_random_seed():
    return int(time.time_ns() % (2**31 - 1))


class Unet3dMediaPipe(MediaPipe):

    """
    Class defining unet media pipe.

    """

    def __init__(
            self,
            a_device=None,
            a_batch_size=1,
            a_prefetch_count=1,
            a_num_instances=1,
            a_instance_id=0,
            a_pipeline=None,
            a_enable_zoom=False,
            a_num_threads=1,
            **kwargs):
        """
        Constructor method.

        :params a_device: media device to run mediapipe on. <hpu/hpu:0>
        :params a_batch_size: mediapipe output batch size.
        :params a_prefetch_count: queue depth for media processing.
        :params a_num_instances: number of devices.
        :params a_instance_id: instance id of current device.
        :params a_pipeline: mediapipe to be created for Unet.<TrainPipeline/BenchmarkPipeline_Train>
        :params a_enable_zoom: whether zoom has to be enabled for TrainPipeline
        :params **kwargs: dictionary of params for Unet3dMediaPipe
        """

        self.batch_size = a_batch_size
        prefetch_count = a_prefetch_count
        self.num_instances = a_num_instances
        self.instance_id = a_instance_id
        self.pipeName = a_pipeline
        self.enable_zoom = a_enable_zoom
        self.dim = kwargs["dim"]
        # seed = kwargs["seed"]
        seed_mediapipe = kwargs.get("seed", None)
        self.patch_size = kwargs["patch_size"]
        self.oversampling = kwargs["oversampling"]  # 0.33
        # self.patch_size = patch_size.copy()
        pipe_drop_last = False
        pipe_reader_pad_remainder = True
        train_shuffle = True
        train_shuffle_across_dataset = True
        benchmark_shuffle = False
        benchmark_shuffle_across_dataset = False
        val_shuffle = False
        val_shuffle_across_dataset = False
        test_shuffle_across_dataset = False
        test_shuffle = False
        image_num_channel = 4
        label_num_channel = 1

        class_pipename = "{}:{}".format(self.__class__.__name__, self.pipeName)
        class_pipename = str(class_pipename)

        super().__init__(device=a_device,
                         prefetch_depth=prefetch_count,
                         batch_size=self.batch_size,
                         num_threads=a_num_threads,
                         pipe_name=class_pipename)

        if (self.pipeName != "TrainPipeline") and (self.pipeName != "BenchmarkPipeline_Train") and (
                self.pipeName != "EvalPipeline") and (self.pipeName != "TestPipeline"):
            raise ValueError(
                "Unet3dMediaPipe: pipe {} not supported!".format(self.pipeName))

        if (self.pipeName == "TestPipeline"):
            input_list = [kwargs["imgs"], kwargs["meta"]]
        else:
            input_list = [kwargs["imgs"], kwargs["lbls"]]

        if (self.pipeName == "TrainPipeline"):
            self.augment = kwargs["augment"]
            set_aug_seed = kwargs["set_aug_seed"]

        # if set_aug_seed is False, generate new seed for augmentation
        # if set_aug_seed is True and seed_mediapipe is available, use it for augmentation
        if (seed_mediapipe is None):
            if (self.num_instances > 1) and (self.pipeName ==
                                             "TrainPipeline") and (train_shuffle_across_dataset):
                raise ValueError(
                    "Unet3dMediaPipe: num_instances > 1, seed not provided!")
            else:
                print("Warning: Unet3dMediaPipe seed not provided, generating seed")

            seed_mediapipe = int(time.time_ns() % (2**31 - 1))
            if (self.pipeName == "TrainPipeline"):
                seed_augment = seed_mediapipe
        else:
            if self.pipeName == "TrainPipeline":
                if not set_aug_seed:
                    seed_augment = int(time.time_ns() % (2**31 - 1))
                else:
                    seed_augment = seed_mediapipe + self.instance_id

        print(
            "Unet3dMediaPipe BFLOAT16 pipeline {} batch_size {} dim {} oversampling {} prefetch_depth {}".format(
                self.pipeName,
                self.batch_size,
                self.dim,
                self.oversampling,
                prefetch_count))

        if self.pipeName == "TrainPipeline":
            print("Unet3dMediaPipe seed {} augment {} set_aug_seed {} augment_seed {} num_instances {} instance_id {}".format(
                seed_mediapipe, self.augment, set_aug_seed, seed_augment, self.num_instances, self.instance_id))

            if not self.augment:
                print("Warning: Unet3dMediaPipe augmentation turned off")

            if self.enable_zoom:
                print("Unet3dMediaPipe zoom enabled")

        else:
            print("Unet3dMediaPipe seed {} num_instances {} instance_id {}".format(
                seed_mediapipe, self.num_instances, self.instance_id))

        if (self.pipeName == "TrainPipeline") or (self.pipeName == "BenchmarkPipeline_Train"):
            if self.dim == 2:
                self.patch_size = self.patch_size[::-1]
                # self.patch_size = [kwargs["batch_size_2d"]] + self.patch_size
                self.patch_size = self.patch_size + [kwargs["batch_size_2d"]]
                print("Unet3dMediaPipe patch size ", self.patch_size[::-1])
            else:
                self.patch_size = self.patch_size[::-1]
                print("Unet3dMediaPipe patch size ", self.patch_size[::-1])

        if (self.pipeName == "TrainPipeline"):
            # ------------reader------------------------------
            self.inputX = fn.ReadNumpyDatasetFromDir(num_outputs=1,
                                                     shuffle=train_shuffle,
                                                     shuffle_across_dataset=train_shuffle_across_dataset,
                                                     file_list=input_list[0],
                                                     dtype=dt.FLOAT32,
                                                     # dense=False,
                                                     seed=seed_mediapipe,
                                                     drop_remainder=pipe_drop_last,
                                                     pad_remainder=pipe_reader_pad_remainder,
                                                     num_slices=self.num_instances,
                                                     slice_index=self.instance_id,
                                                     device='cpu'
                                                     )

            self.inputY = fn.ReadNumpyDatasetFromDir(num_outputs=1,
                                                     shuffle=train_shuffle,
                                                     shuffle_across_dataset=train_shuffle_across_dataset,
                                                     file_list=input_list[1],
                                                     dtype=dt.UINT8,
                                                     # dense=False,
                                                     seed=seed_mediapipe,
                                                     drop_remainder=pipe_drop_last,
                                                     pad_remainder=pipe_reader_pad_remainder,
                                                     num_slices=self.num_instances,
                                                     slice_index=self.instance_id,
                                                     device='cpu'
                                                     )
            # ------------random biased crop------------------------------
            self.rand_bias_crop = fn.RandomBiasedCrop(patch_size=self.patch_size,
                                                      over_sampling=self.oversampling,
                                                      seed=get_random_seed(),
                                                      cache_bboxes=True,
                                                      cache_bboxes_at_first_run=True,
                                                      device='cpu')
            """self.crop_img = fn.Crop(crop_w=self.patch_size[0],
                                    crop_h=self.patch_size[1],
                                    crop_d=self.patch_size[2],
                                    crop_pos_x=0.5,
                                    crop_pos_y=0.5,
                                    crop_pos_z=0.5,
                                    device='cpu')
            self.crop_lbl = fn.Crop(crop_w=self.patch_size[0],
                                    crop_h=self.patch_size[1],
                                    crop_d=self.patch_size[2],
                                    crop_pos_x=0.5,
                                    crop_pos_y=0.5,
                                    crop_pos_z=0.5,
                                    device='cpu')"""
            # [W,H,D,C,N]
            if self.enable_zoom:

                priv_params = {}
                priv_params['prob'] = g_rand_aug_prob
                priv_params['crop_min'] = g_crop_min
                priv_params['crop_max'] = g_crop_max
                priv_params['patch_size'] = self.patch_size

                self.crop_size = fn.MediaFunc(func=random_zoom_func,
                                              shape=[3, self.batch_size],
                                              dtype=dt.UINT32,
                                              seed=get_random_seed(),
                                              priv_params=priv_params)

                self.zoom = fn.Zoom(patch_size=self.patch_size,
                                    num_channels=image_num_channel,
                                    device='cpu')
            # ------------Reshape(for flip)------------------------------
            self.cast_bf16 = fn.Cast(dtype=dt.BFLOAT16, device='hpu')
            # Reshape for flip [ W,H,D,C,N] -> [W,H,D*C,N]
            shape_patch = self.patch_size.copy()  # [W,H,D]
            shape = []
            shape.append(shape_patch[0])
            shape.append(shape_patch[1])
            shape.append(shape_patch[2] * image_num_channel)
            shape.append(self.batch_size)
            self.img_reshape_hflip = fn.Reshape(size=shape,
                                                tensorDim=len(shape),
                                                layout='',
                                                dtype=dt.BFLOAT16, device='hpu')  # img [W,H,D*C,N]
            shape_patch = self.patch_size.copy()  # [W,H,D]
            shape = []
            shape.append(shape_patch[0])
            shape.append(shape_patch[1])
            shape.append(shape_patch[2] * label_num_channel)
            shape.append(self.batch_size)

            self.lbl_reshape_hflip = fn.Reshape(size=shape,
                                                tensorDim=len(shape),
                                                layout='',
                                                dtype=dt.UINT8, device='hpu')  # lbl [W,H,D*C,N]
            # -----------Random Flip-------------------------
            self.random_flip_prob = fn.Constant(
                constant=flip_prob, dtype=dt.FLOAT32, device='cpu')
            # ------------H Flip------------------------------
            # random horizontal flip node
            # a_batch_size
            self.is_hflip = fn.CoinFlip(seed=get_random_seed(
            ), dtype=dt.INT8, device='cpu')  # [[batch_size]]
            self.hflip_reshape_p = fn.Reshape(size=[self.batch_size],
                                              tensorDim=1,
                                              layout='',
                                              dtype=dt.UINT8, device='hpu')  # [batch_size]
            self.img_hflip = fn.RandomFlip(
                horizontal=1, dtype=dt.BFLOAT16, device='hpu')  # img [W,H,D*C,N]
            self.lbl_hflip = fn.RandomFlip(
                horizontal=1, dtype=dt.UINT8, device='hpu')  # lbl [W,H,D*C,N]

            # ------------V Flip------------------------------
            # random vertical flip node
            # a_batch_size
            self.is_vflip = fn.CoinFlip(seed=get_random_seed(
            ), dtype=dt.INT8, device='cpu')  # [[batch_size]]
            self.vflip_reshape_p = fn.Reshape(size=[self.batch_size],
                                              tensorDim=1,
                                              layout='',
                                              dtype=dt.UINT8, device='hpu')  # [batch_size]
            self.img_vflip = fn.RandomFlip(
                vertical=1, dtype=dt.BFLOAT16, device='hpu')  # img [W,H,D*C,N]
            self.lbl_vflip = fn.RandomFlip(
                vertical=1, dtype=dt.UINT8, device='hpu')  # lbl [W,H,D*C,N]

            if self.dim == 3:
                # ------------D Flip------------------------------
                # Reshape for dflip [W,H,D*C,N] -> [W*H,D,C,N]
                shape_patch = self.patch_size.copy()  # [W,H,D]
                shape = []
                shape.append(shape_patch[0] * shape_patch[1])
                shape.append(shape_patch[2])
                shape.append(image_num_channel)
                shape.append(self.batch_size)
                self.img_reshape_dflip = fn.Reshape(
                    size=shape,
                    tensorDim=len(shape),
                    layout='',
                    dtype=dt.BFLOAT16,
                    device='hpu')  # img [W*H,D,C,N]

                shape_patch = self.patch_size.copy()  # [W,H,D]
                shape = []
                shape.append(shape_patch[0] * shape_patch[1])
                shape.append(shape_patch[2])
                shape.append(label_num_channel)
                shape.append(self.batch_size)
                self.lbl_reshape_dflip = fn.Reshape(size=shape,
                                                    tensorDim=len(shape),
                                                    layout='',
                                                    dtype=dt.UINT8, device='hpu')  # lbl [W*H,D,C,N]

                self.is_dflip = fn.CoinFlip(seed=get_random_seed(
                ), dtype=dt.INT8, device='cpu')  # [[batch_size]]
                # a_batch_size
                self.dflip_reshape_p = fn.Reshape(size=[self.batch_size],
                                                  tensorDim=1,
                                                  layout='',
                                                  dtype=dt.UINT8, device='hpu')  # [batch_size]
                self.img_dflip = fn.RandomFlip(
                    vertical=1, dtype=dt.BFLOAT16, device='hpu')  # img [W*H,D,C,N]
                self.lbl_dflip = fn.RandomFlip(
                    vertical=1, dtype=dt.UINT8, device='hpu')  # lbl [W*H,D,C,N]
                # Reshape [W*H,D,C,N] -> [W,H,D*C,N]
                shape_patch = self.patch_size.copy()  # [W,H,D]
                shape = []
                shape.append(shape_patch[0])
                shape.append(shape_patch[1])
                shape.append(shape_patch[2] * image_num_channel)
                shape.append(self.batch_size)
                self.img_reshape_noise = fn.Reshape(
                    size=shape,
                    tensorDim=len(shape),
                    layout='',
                    dtype=dt.BFLOAT16,
                    device='hpu')  # img [W,H,D*C,N]

            # ------------Gaussian noise------------------------------

            self.g_noise_prob = fn.Constant(
                constant=g_rand_aug_prob, dtype=dt.FLOAT32, device="cpu")

            self.is_gnoise = fn.CoinFlip(
                seed=get_random_seed(), dtype=dt.INT8, device="cpu")  # [[batch_size]]

            self.default_std_dev = fn.Constant(
                constant=0.0, dtype=dt.FLOAT32, device="cpu")

            self.random_std_dev = fn.RandomUniform(
                seed=get_random_seed(),
                low=g_min_std_dev,
                high=g_max_std_dev,
                dtype=dt.FLOAT32,
                device='cpu')

            self.where_gnoise = fn.Where(
                dtype=dt.FLOAT32, device="cpu")  # [[batch_size]]
            # a_batch_size
            self.std_dev_reshape = fn.Reshape(size=[self.batch_size],
                                              tensorDim=1,
                                              layout='',
                                              dtype=dt.FLOAT32, device='hpu')  # [batch_size]

            shape_patch = self.patch_size.copy()  # [W,H,D]
            shape = []
            shape.append(shape_patch[0])
            shape.append(shape_patch[1])
            shape.append(shape_patch[2] * image_num_channel)
            shape.append(self.batch_size)
            self.rnd_normal = fn.RandomNormal(mean=0.0,
                                              stddev=0.1,
                                              seed=get_random_seed(),
                                              dtype=dt.BFLOAT16,
                                              dims=len(shape),
                                              shape=shape, device='hpu')  # noise [W,H,D*C,N]
            # img [W,H,D*C,N]
            self.add = fn.Add(dtype=dt.BFLOAT16, device='hpu')

            # Gaussian Blur--------------------------------------------------
            # Reshape [W,H,D*C,N] -> [W,H,D,C,N]
            shape = self.patch_size.copy()  # [W,H,D]
            shape.append(image_num_channel)
            shape.append(self.batch_size)
            self.img_reshape_transpose_pre_blur = fn.Reshape(size=shape,
                                                             tensorDim=len(
                                                                 shape),
                                                             layout='',
                                                             dtype=dt.BFLOAT16,
                                                             device='hpu')  # img [W,H,D,C,N]

            self.g_blur_prob = fn.Constant(
                constant=g_rand_aug_prob, dtype=dt.FLOAT32, device="cpu")

            self.is_g_blur = fn.CoinFlip(
                seed=get_random_seed(), dtype=dt.INT8, device="cpu")

            self.default_gb_sigma = fn.Constant(
                constant=0.0, dtype=dt.FLOAT32, device="cpu")

            self.random_gb_sigma = fn.RandomUniform(
                seed=get_random_seed(),
                low=g_min_sigma,
                high=g_max_sigma,
                dtype=dt.FLOAT32,
                device='cpu')

            self.where_g_blur = fn.Where(dtype=dt.FLOAT32, device="cpu")

            shape = self.patch_size.copy()  # [W,H,D]
            shape.append(image_num_channel)
            shape.append(self.batch_size)
            self.gaussian_blur = fn.GaussianBlur(
                max_sigma=g_max_sigma,
                min_sigma=g_min_sigma,
                shape=shape,
                dtype=dt.BFLOAT16,
                device="hpu")

            # ------------Brightness------------------------------
            # self.cast_fp32 = fn.Cast(dtype=dt.FLOAT32,device='hpu')
            # Reshape [W,H,D,C,N] ->  [W,H,D*C,N]
            shape_patch = self.patch_size.copy()  # [W,H,D]
            shape = []
            shape.append(shape_patch[0])
            shape.append(shape_patch[1])
            shape.append(shape_patch[2] * image_num_channel)
            shape.append(self.batch_size)
            self.img_reshape_brightness = fn.Reshape(size=shape, tensorDim=len(
                shape), layout='', dtype=dt.BFLOAT16, device='hpu')  # img [W,H,D*C,N]

            self.random_b_scale = fn.RandomUniform(
                seed=get_random_seed(),
                low=g_brt_factor_min,
                high=g_brt_factor_max,
                dtype=dt.FLOAT32,
                device='cpu')
            self.default_b_scale = fn.Constant(
                constant=1.0, dtype=dt.FLOAT32, device='cpu')

            self.prob_brightness = fn.Constant(
                constant=g_rand_aug_prob, dtype=dt.FLOAT32, device='cpu')
            self.is_brightness = fn.CoinFlip(
                seed=get_random_seed(), dtype=dt.INT8, device='cpu')
            self.where_brigtness = fn.Where(
                dtype=dt.FLOAT32, device='cpu')  # [[batch_size]]
            # a_batch_size
            self.img_reshape_where = fn.Reshape(size=[self.batch_size],
                                                tensorDim=1,
                                                layout='',
                                                dtype=dt.FLOAT32, device='hpu')  # [batch_size]

            self.brightness = fn.Brightness(
                dtype=dt.BFLOAT16, device='hpu')  # img [W,H,D*C,N]
            # ------------Contrast------------------------------
            shape = self.patch_size.copy()  # [WHD]
            shape.append(image_num_channel)  # [WHDC]
            shape.append(self.batch_size)  # [WHDN]
            self.img_reshape_contrast_input = fn.Reshape(size=shape, tensorDim=len(
                shape), layout='', dtype=dt.BFLOAT16, device='hpu')  # img [W,H,D,C,N]

            self.random_c_scale = fn.RandomUniform(
                seed=get_random_seed(),
                low=g_scale_min,
                high=g_scale_max,
                dtype=dt.FLOAT32,
                device='cpu')

            self.default_c_scale = fn.Constant(
                constant=1.0, dtype=dt.FLOAT32, device='cpu')

            self.prob_contrast = fn.Constant(
                constant=g_rand_aug_prob, dtype=dt.FLOAT32, device='cpu')

            self.is_contrast = fn.CoinFlip(
                seed=get_random_seed(), dtype=dt.INT8, device='cpu')

            self.where_contrast = fn.Where(dtype=dt.FLOAT32, device='cpu')

            self.cast_scale = fn.Cast(dtype=dt.BFLOAT16, device='hpu')

            self.min = fn.ReduceMin(
                reductionDimension=[3, 2, 1, 0], dtype=dt.BFLOAT16, device='hpu')
            self.max = fn.ReduceMax(
                reductionDimension=[3, 2, 1, 0], dtype=dt.BFLOAT16, device='hpu')

            shape = []
            shape.append(
                self.patch_size[0] * self.patch_size[1] * self.patch_size[2] * image_num_channel)
            shape.append(self.batch_size)
            self.img_reshape_before_mul = fn.Reshape(size=shape,
                                                     tensorDim=2,
                                                     layout='',
                                                     dtype=dt.BFLOAT16, device='hpu')  # [W*H*D*C,N]

            self.mul = fn.Mult(dtype=dt.BFLOAT16, device='hpu')

            shape = self.patch_size.copy()  # [WHD]
            shape.append(image_num_channel)  # [WHDC]
            shape.append(self.batch_size)  # [WHDN]
            self.img_reshape_after_mul = fn.Reshape(size=shape, tensorDim=len(
                shape), layout='', dtype=dt.BFLOAT16, device='hpu')  # img [W,H,D,C,N]

            self.clamp = fn.Clamp(dtype=dt.BFLOAT16, device='hpu')

            # ------------Reshape------------------------------
            # [W*H*D*C,N] -> [W,H,D,C,N]
            shape = self.patch_size.copy()
            shape.append(image_num_channel)
            shape.append(self.batch_size)
            self.img_reshape_output = fn.Reshape(size=shape,
                                                 tensorDim=len(shape),
                                                 layout='',
                                                 dtype=dt.BFLOAT16, device='hpu')  # img [W,H,D,C,N]

            shape = self.patch_size.copy()
            shape.append(label_num_channel)
            shape.append(self.batch_size)
            self.lbl_reshape_output = fn.Reshape(size=shape,
                                                 tensorDim=len(shape),
                                                 layout='',
                                                 dtype=dt.UINT8, device='hpu')  # lbl [W,H,D,C,N]

            if self.dim == 2:
                # ------------Transpose------------------------------
                # [W,H,D,C,N] -> [W,H,C,D,N]
                self.img_transpose = fn.Transpose(
                    permutation=[
                        0,
                        1,
                        3,
                        2,
                        4],
                    tensorDim=5,
                    dtype=dt.BFLOAT16,
                    device='hpu')  # img [W,H,C,D,N]
                self.lbl_transpose = fn.Transpose(permutation=[0, 1, 3, 2, 4],
                                                  tensorDim=5,
                                                  dtype=dt.UINT8, device='hpu')  # lbl [W,H,C,D,N]

        elif (self.pipeName == "BenchmarkPipeline_Train"):
            self.inputX = fn.ReadNumpyDatasetFromDir(num_outputs=1,
                                                     shuffle_across_dataset=benchmark_shuffle_across_dataset,
                                                     shuffle=benchmark_shuffle,
                                                     file_list=input_list[0],
                                                     dtype=dt.FLOAT32,
                                                     # dense=False,
                                                     seed=seed_mediapipe,
                                                     drop_remainder=pipe_drop_last,
                                                     pad_remainder=pipe_reader_pad_remainder,
                                                     num_slices=self.num_instances,
                                                     slice_index=self.instance_id,
                                                     device='cpu'
                                                     )
            self.inputY = fn.ReadNumpyDatasetFromDir(num_outputs=1,
                                                     shuffle_across_dataset=benchmark_shuffle_across_dataset,
                                                     shuffle=benchmark_shuffle,
                                                     file_list=input_list[1],
                                                     dtype=dt.UINT8,
                                                     # dense=False,
                                                     seed=seed_mediapipe,
                                                     drop_remainder=pipe_drop_last,
                                                     pad_remainder=pipe_reader_pad_remainder,
                                                     num_slices=self.num_instances,
                                                     slice_index=self.instance_id,
                                                     device='cpu'
                                                     )

            self.crop_img = fn.Crop(crop_w=self.patch_size[0],
                                    crop_h=self.patch_size[1],
                                    crop_d=self.patch_size[2],
                                    crop_pos_x=0.5,
                                    crop_pos_y=0.5,
                                    crop_pos_z=0.5,
                                    device='cpu')
            self.crop_lbl = fn.Crop(crop_w=self.patch_size[0],
                                    crop_h=self.patch_size[1],
                                    crop_d=self.patch_size[2],
                                    crop_pos_x=0.5,
                                    crop_pos_y=0.5,
                                    crop_pos_z=0.5,
                                    device='cpu')
            self.cast_bf16 = fn.Cast(dtype=dt.BFLOAT16, device='hpu')
            shape = self.patch_size.copy()
            shape.append(image_num_channel)
            shape.append(self.batch_size)
            self.img_reshape_output = fn.Reshape(size=shape,
                                                 tensorDim=len(shape),
                                                 layout='',
                                                 dtype=dt.BFLOAT16, device='hpu')
            shape = self.patch_size.copy()
            shape.append(label_num_channel)
            shape.append(self.batch_size)
            self.lbl_reshape_output = fn.Reshape(size=shape,
                                                 tensorDim=len(shape),
                                                 layout='',
                                                 dtype=dt.UINT8, device='hpu')
            if self.dim == 2:
                # [W,H,D,C,N] -> [W,H,C,D,N]
                self.img_transpose = fn.Transpose(permutation=[0, 1, 3, 2, 4],
                                                  tensorDim=5,
                                                  dtype=dt.BFLOAT16, device='hpu')
                self.lbl_transpose = fn.Transpose(permutation=[0, 1, 3, 2, 4],
                                                  tensorDim=5,
                                                  dtype=dt.UINT8, device='hpu')

        elif (self.pipeName == "EvalPipeline"):
            self.inputX = fn.ReadNumpyDatasetFromDir(num_outputs=1,
                                                     shuffle_across_dataset=val_shuffle_across_dataset,
                                                     shuffle=val_shuffle,
                                                     file_list=input_list[0],
                                                     dtype=dt.FLOAT32,
                                                     # dense=False,
                                                     seed=seed_mediapipe,
                                                     drop_remainder=pipe_drop_last,
                                                     pad_remainder=pipe_reader_pad_remainder,
                                                     num_slices=self.num_instances,
                                                     slice_index=self.instance_id,
                                                     device='cpu'
                                                     )
            self.inputY = fn.ReadNumpyDatasetFromDir(num_outputs=1,
                                                     shuffle_across_dataset=val_shuffle_across_dataset,
                                                     shuffle=val_shuffle,
                                                     file_list=input_list[1],
                                                     dtype=dt.UINT8,
                                                     # dense=False,
                                                     seed=seed_mediapipe,
                                                     drop_remainder=pipe_drop_last,
                                                     pad_remainder=pipe_reader_pad_remainder,
                                                     num_slices=self.num_instances,
                                                     slice_index=self.instance_id,
                                                     device='cpu'
                                                     )
            # self.cast_bf16 = fn.Cast(dtype=dt.BFLOAT16,device='hpu')
        elif (self.pipeName == "TestPipeline"):
            self.inputX = fn.ReadNumpyDatasetFromDir(num_outputs=1,
                                                     shuffle_across_dataset=test_shuffle_across_dataset,
                                                     shuffle=test_shuffle,
                                                     file_list=input_list[0],
                                                     dtype=dt.FLOAT32,
                                                     # dense=False,
                                                     seed=seed_mediapipe,
                                                     drop_remainder=pipe_drop_last,
                                                     pad_remainder=pipe_reader_pad_remainder,
                                                     num_slices=self.num_instances,
                                                     slice_index=self.instance_id,
                                                     device='cpu'
                                                     )
            self.inputMeta = fn.ReadNumpyDatasetFromDir(num_outputs=1,
                                                        shuffle_across_dataset=test_shuffle_across_dataset,
                                                        shuffle=test_shuffle,
                                                        file_list=input_list[1],
                                                        dtype=dt.INT64,
                                                        # dense=False,
                                                        seed=seed_mediapipe,
                                                        drop_remainder=pipe_drop_last,
                                                        pad_remainder=pipe_reader_pad_remainder,
                                                        num_slices=self.num_instances,
                                                        slice_index=self.instance_id,
                                                        device='cpu'
                                                        )
            # self.cast_bf16 = fn.Cast(dtype=dt.BFLOAT16,device='hpu')
        else:
            raise ValueError(
                "Unet3dMediaPipe: pipe {} not supported!".format(self.pipeName))

    def definegraph(self):
        """
        Method defines the media graph.

        :returns : output images, labels
        """
        if (self.pipeName == "TrainPipeline"):

            img = self.inputX()
            lbl = self.inputY()

            img, lbl, coord = self.rand_bias_crop(img, lbl)  # ToDo: coord
            # img = self.crop_img(img)  # [W,H,D,C,N]
            # lbl = self.crop_lbl(lbl)
            if self.augment:

                if self.enable_zoom:
                    crop_size_zoom = self.crop_size()
                    img, lbl = self.zoom(img, lbl, crop_size_zoom)
                img = self.cast_bf16(img)
                # ------------H Flip------------------------------
                img, lbl = self.img_reshape_hflip(img), self.lbl_reshape_hflip(
                    lbl)  # reshape output [W,H,D*C,N]
                rflip_prob = self.random_flip_prob()
                h_predicate = self.is_hflip(rflip_prob)
                h_predicate = self.hflip_reshape_p(h_predicate)
                img, lbl = self.img_hflip(
                    img, h_predicate), self.lbl_hflip(lbl, h_predicate)
                # ------------V Flip------------------------------
                v_predicate = self.is_vflip(rflip_prob)
                v_predicate = self.vflip_reshape_p(v_predicate)
                img, lbl = self.img_vflip(
                    img, v_predicate), self.lbl_vflip(lbl, v_predicate)
                if self.dim == 3:
                    # ------------D Flip------------------------------
                    d_predicate = self.is_dflip(rflip_prob)
                    d_predicate = self.dflip_reshape_p(d_predicate)
                    img, lbl = self.img_reshape_dflip(
                        img), self.lbl_reshape_dflip(lbl)  # reshape output [W*H,D,C,N]
                    img, lbl = self.img_dflip(
                        img, d_predicate), self.lbl_dflip(lbl, d_predicate)

                    # reshape output [W,H,D*C,N]
                    img = self.img_reshape_noise(img)

            # ------------Gaussian noise------------------------------
                gn_prob = self.g_noise_prob()
                g_noise_predicate = self.is_gnoise(gn_prob)  # coin flip
                std_dev_def = self.default_std_dev()
                std_dev_rand = self.random_std_dev()
                std_dev = self.where_gnoise(
                    g_noise_predicate, std_dev_rand, std_dev_def)
                std_dev = self.std_dev_reshape(std_dev)
                # gn_seed = self.noise_seed()
                # gn_seed = self.noise_seed_reshape(gn_seed)
                # noise = self.rnd_normal(std_dev, gn_seed)
                noise = self.rnd_normal(std_dev)  # ---working
                img = self.add(img, noise)

                # ------------Gaussian blur------------------------------
                img = self.img_reshape_transpose_pre_blur(
                    img)  # reshape output [W,H,D,C,N]
                is_blur = self.g_blur_prob()
                gb_predicate = self.is_g_blur(is_blur)
                gb_sigma_def = self.default_gb_sigma()
                gb_sigma_rand = self.random_gb_sigma()
                gb_sigma = self.where_g_blur(
                    gb_predicate, gb_sigma_rand, gb_sigma_def)

                # gaussian blur
                img = self.gaussian_blur(img, gb_sigma)
                # ------------Brightness------------------------------
                img = self.img_reshape_brightness(img)
                # reshape output  [W,H,(D*C),N]
                scale_rand_b = self.random_b_scale()  # unifoorm
                scale_def_b = self.default_b_scale()  # 1.0
                prob_b = self.prob_brightness()
                predicate_b = self.is_brightness(prob_b)
                scale_b = self.where_brigtness(
                    predicate_b, scale_rand_b, scale_def_b)
                scale_b = self.img_reshape_where(scale_b)
                img = self.brightness(img, scale_b)  # [W,H,(D*C),N]
                # ------------Contrast------------------------------
                # img = self.cast_bf16(img)
                img = self.img_reshape_contrast_input(img)  # [W,H,D,C,N]
                scale_rand_c = self.random_c_scale()  # unifoorm
                scale_def_c = self.default_c_scale()  # 1.0
                prob_c = self.prob_contrast()
                predicate_c = self.is_contrast(prob_c)
                scale_c = self.where_contrast(
                    predicate_c, scale_rand_c, scale_def_c)
                scale_c = self.cast_scale(scale_c)
                min0_c, min_i = self.min(img)
                max0_c, max_i = self.max(img)
                img = self.img_reshape_before_mul(img)
                img = self.mul(img, scale_c)
                img = self.img_reshape_after_mul(img)
                img = self.clamp(img, min0_c, max0_c)

            # ------------Reshape------------------------------
            img, lbl = self.img_reshape_output(img), self.lbl_reshape_output(
                lbl)  # reshape output [W,H,D,C,N]

            if self.dim == 2:
                # ------------Transpose------------------------------
                # [W,H,D,C,N] -> [W,H,C,D,N]
                img, lbl = self.img_transpose(img), self.lbl_transpose(lbl)

            return img, lbl

        elif (self.pipeName == "BenchmarkPipeline_Train"):
            img = self.inputX()
            lbl = self.inputY()

            # img, lbl, coord = self.rand_bias_crop(img, lbl)
            img = self.crop_img(img)
            lbl = self.crop_lbl(lbl)
            img = self.cast_bf16(img)
            img, lbl = self.img_reshape_output(
                img), self.lbl_reshape_output(lbl)  # reshape output [W,H,D,C,N]

            if self.dim == 2:
                # [W,H,D,C,N] -> [W,H,C,D,N]
                img, lbl = self.img_transpose(img), self.lbl_transpose(lbl)

            return img, lbl

        elif (self.pipeName == "EvalPipeline"):
            img = self.inputX()
            lbl = self.inputY()
            # img = self.cast_bf16(img)
            img.as_hpu()
            lbl.as_hpu()
            return img, lbl
        elif (self.pipeName == "TestPipeline"):
            img = self.inputX()
            meta = self.inputMeta()
            # img = self.cast_bf16(img)
            img.as_hpu()
            meta.as_hpu()
            return img, meta
        else:
            raise ValueError(
                "Unet3dMediaPipe: pipe {} not supported!".format(self.pipeName))

##################################################


class random_zoom_func(media_function):
    """
    Class to randomly generate crop shape for zoom.

    """

    def __init__(self, params):
        """
        Constructor method.

        :params params: random_zoom_func specific params.
                        shape: output shape
                        dtype: output data type
                        seed: seed to be used
                        priv_params: private params for random_zoom_func
                                     crop_min: min crop factor.
                                     crop_max: max crop factor.
                                     prob: probability for crop.
                                     patch_size : patch size.
        """
        self.np_shape = params['shape'][::-1]
        self.np_dtype = params['dtype']
        self.batch_size = self.np_shape[0]
        self.seed = params['seed'] + params['unique_number']
        self.priv_params = params['priv_params']
        self.crop_min = self.priv_params['crop_min']
        self.crop_max = self.priv_params['crop_max']
        self.prob = self.priv_params['prob']
        self.patch_size = self.priv_params['patch_size'].copy()
        self.patch_size_ar = np.array(self.patch_size, dtype=self.np_dtype)
        self.rng = np.random.default_rng(self.seed)

    def __call__(self):
        """
        Callable class method.

        :returns : randomly generated crop shape
        """
        apply_zoom = self.rng.choice(
            [0, 1], p=[(1 - self.prob), self.prob], size=[self.batch_size])
        crop_factor = self.rng.uniform(
            low=self.crop_min, high=self.crop_max, size=[self.batch_size])
        # crop_factor = np.array(crop_factor, dtype=dt.FLOAT32)

        cropped_patch_ar = np.zeros(self.np_shape, dtype=self.np_dtype)

        for i in range(self.batch_size):
            if apply_zoom[i] == 1:
                cropped_patch_ar[i] = np.array(
                    self.patch_size_ar * crop_factor[i], dtype=self.np_dtype)
            else:
                cropped_patch_ar[i] = self.patch_size_ar

        return cropped_patch_ar
