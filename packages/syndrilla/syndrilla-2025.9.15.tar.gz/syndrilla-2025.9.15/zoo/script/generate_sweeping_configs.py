from syndrilla.utils import read_yaml, write_yaml
from collections import OrderedDict
import os, shutil, copy, itertools, argparse
from loguru import logger


def clean_dir(base_path: str):
    base_path = base_path if base_path.endswith('/') else base_path + '/'
    generated_path = f'{base_path}generated/'
    shutil.rmtree(generated_path, ignore_errors=True)


def generate_decoder(base_path: str, code, check_type, distance, dtype, decoder):
    """
        Generate decoder yaml file from examples
    """
    base_path = base_path if base_path.endswith('/') else base_path + '/'
    template_path = 'examples/alist/'
    generated_path = base_path

    configuration_dict = template_path + f'{decoder}_{check_type}.decoder.yaml'

    target_file = os.path.join(generated_path, f'{decoder}_{check_type}.decoder.yaml')

    # Read, modify, and write
    config = read_yaml(configuration_dict)
    if 'decoder' in config:
        config['decoder']['dtype'] = dtype
        config['decoder']['check_type'] = check_type
        if code == 'surface':
            config['decoder']['max_iter'] = distance*2*(distance-1)+1
        else:
            config['decoder']['max_iter'] = distance*2*(distance)
        config['decoder']['parity_matrix_hx'] = base_path + 'hx.matrix.yaml'
        config['decoder']['parity_matrix_hz'] = base_path + 'hz.matrix.yaml'
        config['decoder']['logical_check_matrix'] = True
        config['decoder']['logical_check_lx'] = base_path + 'lx.matrix.yaml'
        config['decoder']['logical_check_lz'] = base_path + 'lz.matrix.yaml'

    write_yaml(target_file, config)


def generate_matrix(base_path: str, code, distance):
    """
        Generate matrix yaml files from examples
    """
    base_path = base_path if base_path.endswith('/') else base_path + '/'
    template_path = 'examples/alist/'
    generated_path = base_path

    check_type_list = ['hx', 'hz', 'lx', 'lz']

    # create all hx, hz, lx, lz matrix yaml files 
    for check_type in check_type_list:
        configuration_dict = template_path + f'{check_type}.matrix.yaml'
        target_file = os.path.join(generated_path, f'{check_type}.matrix.yaml')

        # Read, modify, and write
        config = read_yaml(configuration_dict)
        if 'matrix' in config:
            config['matrix']['path'] = f'examples/alist/{code}/{code}_{distance}_{check_type}.alist'
        write_yaml(target_file, config)


def generate_error(base_path: str, probability):
    """
        Generate error yaml file from examples
    """
    base_path = base_path if base_path.endswith('/') else base_path + '/'
    template_path = 'examples/alist/'
    generated_path = base_path
    
    configuration_dict = template_path + 'bsc.error.yaml'
    target_file = os.path.join(generated_path, 'bsc.error.yaml')

    # Read, modify, and write
    config = read_yaml(configuration_dict)
    if 'error' in config:
        config['error']['rate'] = probability
    write_yaml(target_file, config)


def generate_syndrome(base_path: str):
    """
        Generate syndrome yaml file from examples
    """
    base_path = base_path if base_path.endswith('/') else base_path + '/'
    template_path = 'examples/alist/'
    generated_path = base_path
    
    configuration_dict = template_path + 'perfect.syndrome.yaml'
    target_file = os.path.join(generated_path, 'perfect.syndrome.yaml')

    # Read, and write
    config = read_yaml(configuration_dict)
    write_yaml(target_file, config)


def generate_checker(base_path: str, check_type):
    """
        Generate logical check yaml file from examples
    """
    base_path = base_path if base_path.endswith('/') else base_path + '/'
    template_path = 'examples/alist/'
    generated_path = base_path

    if check_type == 'hx':
        configuration_dict = template_path + 'lx.check.yaml'
        target_file = os.path.join(generated_path, 'lx.check.yaml')
    else:
        configuration_dict = template_path + 'lz.check.yaml'
        target_file = os.path.join(generated_path, 'lz.check.yaml')

    # Read, write
    config = read_yaml(configuration_dict)
    write_yaml(target_file, config)


def generate_checker(base_path: str, check_type):
    """
        Generate logical check yaml file from examples
    """
    base_path = base_path if base_path.endswith('/') else base_path + '/'
    template_path = 'examples/alist/'
    generated_path = base_path

    if check_type == 'hx':
        configuration_dict = template_path + 'lx.check.yaml'
        target_file = os.path.join(generated_path, 'lx.check.yaml')
    else:
        configuration_dict = template_path + 'lz.check.yaml'
        target_file = os.path.join(generated_path, 'lz.check.yaml')

    # Read, write
    config = read_yaml(configuration_dict)
    write_yaml(target_file, config)


def parse_commandline_args():
    """
    parse command line inputs
    """
    parser = argparse.ArgumentParser(
        description='Generate sweeping configurations.')
    parser.add_argument('-r', '--run_dir', type=str, default=None,
                        help = 'The run directory to store outputs. This should be a sub directory under zoo.')

    return parser.parse_args()


def main():
    args = parse_commandline_args()

    logger.remove()
    base_dir = 'zoo/'
    config_list = read_yaml(base_dir + 'script/sweeping_configs.yaml')
    # load each different code settings from sweeping_configs.yaml file
    for decoder in config_list['decoder']:
        for code in config_list['code']:
            for check_type in config_list['check_type']:
                for distance in config_list['distance']:
                    for dtype in config_list['dtype']:
                        for probability in config_list['probability']:
                            if args.run_dir is None:
                                dir_name = f'{decoder}_sweeping/{code}_{check_type}_{probability}_{distance}_{dtype}'
                            else:
                                dir_name = f'{args.run_dir}/{code}_{check_type}_{probability}_{distance}_{dtype}'
                            base_path = os.path.join(base_dir, dir_name)
                            os.makedirs(base_path, exist_ok=True)
                            # clean up directionary
                            clean_dir(base_path)
                            if os.path.isdir(base_path):
                                # create each yaml files
                                generate_decoder(base_path, code, check_type, distance, dtype, decoder)
                                generate_syndrome(base_path)
                                generate_error(base_path, probability)
                                generate_matrix(base_path, code, distance)
                                generate_checker(base_path, check_type)
                                

if __name__ == '__main__':
    main()