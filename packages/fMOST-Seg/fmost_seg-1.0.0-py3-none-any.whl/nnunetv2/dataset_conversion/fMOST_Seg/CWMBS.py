from nnunetv2.paths import nnUNet_raw
from pathlib import Path
from batchgenerators.utilities.file_and_folder_operations import *
import multiprocessing
import shutil
from tqdm import tqdm
from nnunetv2.dataset_conversion.generate_dataset_json import generate_dataset_json
from tifffile import imread, imwrite

labels = {'background': 0, 'neuron': 1}

def load_and_convert_case(
        input_image: str, 
        input_seg: str, 
        input_dist: str,
        input_swc: str, 
        output_image: str, 
        output_seg: str,  
        output_dist: str,
        output_swc: str):
    
    shutil.copy(input_image, output_image)
    imwrite(output_seg, (imread(input_seg) / 255).astype('uint8'))
    shutil.copy(input_dist, output_dist)
    shutil.copy(input_swc, output_swc)


if __name__ == "__main__":
    root = Path(nnUNet_raw)
    source = '/media/sda1/eason/CWMBS'
    source = Path(source)
    dataset_num = 990
    dataset_num = str(dataset_num).zfill(3)
    assert len(dataset_num) == 3
    dataset_name = f'Dataset{dataset_num}_CWMBS'

    imagestr = root / dataset_name / 'imagesTr'
    imagests = root / dataset_name / 'imagesTs'
    labelstr = root / dataset_name / 'labelsTr'
    labelsts = root / dataset_name / 'labelsTs'
    disttr = root / dataset_name / 'distTr'
    distts = root / dataset_name / 'distTs'
    swcstr = root / dataset_name / 'swcTr'
    swcsts = root / dataset_name / 'swcTs'

    maybe_mkdir_p(imagestr)
    maybe_mkdir_p(imagests)
    maybe_mkdir_p(labelstr)
    maybe_mkdir_p(labelsts)
    maybe_mkdir_p(disttr)
    maybe_mkdir_p(distts)
    maybe_mkdir_p(swcstr)
    maybe_mkdir_p(swcsts)

    train_names = []
    test_names = []

    train_names = [file.name for file in imagestr.glob('*.tif')]
    test_names = [file.name for file in imagests.glob('*.tif')]

    train_datas = [
        (
            source / 'train' / 'images' / name,
            source / 'train' / 'masks' / name,
            source / 'train' / 'dists' / name,
            source / 'train' / 'swcs' / name.replace('.tif', '.swc')
        ) for name in os.listdir(source / 'train' / 'images')
    ]

    test_datas = [
        (
            source / 'test' / 'images' / name,
            source / 'test' / 'masks' / name,
            source / 'test' / 'dists' / name,
            source / 'test' / 'swcs' / name.replace('.tif', '.swc')
        ) for name in os.listdir(source / 'test' / 'images')
    ]

    r = []
    with multiprocessing.get_context("spawn").Pool(multiprocessing.cpu_count()) as p:
        for img, anno, dist, swc in train_datas:
            r.append(
                p.starmap_async(
                    load_and_convert_case,
                    ((
                        img, 
                        anno,
                        dist,
                        swc,
                        imagestr / '{}_0000.tif'.format(img.name.split('.')[0]),
                        labelstr / anno.name,
                        disttr / dist.name,
                        swcstr / swc.name
                    ),)
                )
            )

        for img, anno, dist, swc in test_datas:
            r.append(
                p.starmap_async(
                    load_and_convert_case,
                    ((
                        img, 
                        anno,
                        dist,
                        swc,
                        imagests / '{}_0000.tif'.format(img.name.split('.')[0]),
                        labelsts / anno.name,
                        distts / dist.name,
                        swcsts / swc.name
                    ),)
                )
            )

        for i in tqdm(r):
            i.get()

    generate_dataset_json(root / dataset_name, {0: 'fmost'}, labels,
                          len(train_datas), '.tif', dataset_name=dataset_name, overwrite_image_reader_writer='Tiff3DIO')
    
