import os.path
from sys import argv as sys_argv, executable

# 调试用
# sys_argv.append(r'D:\Cache\CloudCache\Cache')

if len(sys_argv) <= 1:  # 如未给定文件路径则退出
    exit(-1)

# 掩码
Mask = 0xA3  # 163

# 程序所在目录
exe_path = os.path.split(executable)[0]

# 待转码文件的路径
path = sys_argv[1]

# 转码后文件的保存位置
music_save_path = f'{exe_path}\\music'

# 待转码的文件路径列表
file_path_list = []

print('程序所在路径:', exe_path)
print('目标文件路径:', path)


def decode(bytearr):  # 解码
    decode_bytes = bytearray()
    for _b in bytearr:
        decode_bytes.append(_b ^ Mask)
    return decode_bytes


def decode_file(_path):  # 解码文件
    with open(_path, 'rb') as _f:
        return decode(_f.read())


def save_file(_path, _bytes):  # 保存数据到文件
    with open(_path, 'wb') as _f:
        _f.write(_bytes)


def data_dumps(_file_path):     # 将文件内容作为程序执行, 这里用来将json对象转化为python的对象, ps: 为了减少依赖
    try:
        if not os.path.exists(_file_path):
            return None
        with open(_file_path, 'r', encoding='utf-8') as _f:
            __json_dict = {}
            exec('__json_dict=' + _f.read().replace('true', 'True').replace('false', 'False').replace('null', 'None'))
            return __json_dict
    except Exception as _e:
        raise _e


def verify_file_size(_file_path):   # 校验文件大小
    current_file_size = os.path.getsize(_file_path)
    _dict = data_dumps(replace_suffix(_file_path, '.idx'))
    if not _dict:
        return True
    return _dict['size'] == current_file_size


def get_file_suffix(_file_path):    # 获取info文件描述中的后缀名
    _dict = data_dumps(replace_suffix(_file_path, '.info'))
    if not _dict:
        return 'mp3'
    return _dict['format']


def form_path(_file_path):      # 解析文件路径
    _path, _full_file_name = os.path.split(_file_path)
    _file_name, _, _suffix = _full_file_name.rpartition('.')
    return _path, _file_name, _suffix


def replace_suffix(_file_path, _suffix):    # 替换文件后缀
    _path, _file_name = form_path(_file_path)[:2]
    return f'{_file_path}.{_file_name}.{_suffix}'


try:
    # 判断路径是否为文件
    if os.path.isfile(path):
        # 如给定路径是文件, 则将文件添加到待处理列表
        file_path_list.append(path)
    else:
        # 如给定路径是文件夹, 则获取该目录下所有文件, 并添加到待处理列表
        for fn in os.listdir(path):
            if os.path.isfile(f'{path}/{fn}'):
                file_path_list.append(f'{path}/{fn}')

    if not os.path.exists(music_save_path):
        # 如果music文件夹不存在,则创建
        os.makedirs(music_save_path)

    for file_path in file_path_list:
        if not file_path.endswith('.uc'):
            # 如后缀不是uc则跳过
            continue

        # 分割出文件名及后缀
        file_name, suffix = form_path(file_path)[1:]

        # 文件名格式解析如下, ? 表示未知, id即music_id
        # 65766-320-f15db921905b7dc7be3b5c8ab28f49d4
        # id    ?   ?

        # 校验文件大小
        if not verify_file_size(file_path):
            raise SystemError('文件大小与idx文件中描述不符')

        # 使用music_id获取歌曲的信息
        music_name = None   # get_music_name(file_name.split('-')[0])
        # 获取歌曲后缀
        music_file_suffix = get_file_suffix(file_path)
        print('正在进行转码: %s.uc' % file_name)
        print('已通过idx文件校验大小, info文件中描述后缀为.%s\n' % music_file_suffix)

        # 构建保存文件的路径及文件名
        save_path = f'{music_save_path}/{music_name or file_name}.{music_file_suffix}'
        # 解码并写入解码后的数据到文件
        save_file(save_path, decode_file(file_path))

except Exception as e:
    # 输出错误信息
    print(e)
    os.system('pause')
