import io
import getopt
import json
import os
import sys
from typing import Dict, Any
from contextlib import contextmanager
from dotenv.main import DotEnv, load_dotenv


def _fix_dotenv():
    def my_get_stream(self):
        """重写python-dotenv读取文件的方法，使用utf-8，支持读取中文"""
        if isinstance(self.dotenv_path, io.StringIO):
            yield self.dotenv_path
        elif os.path.isfile(self.dotenv_path):
            with io.open(self.dotenv_path, encoding='utf-8') as stream:
                yield stream
        else:
            if self.verbose:
                print("File doesn't exist %s", self.dotenv_path)
            yield io.StringIO('')

    DotEnv._get_stream = contextmanager(my_get_stream)


def get_cmd_opts() -> Dict[str, Any]:
    """
    get commandline opts
    :return: cmd options
    """
    # get options
    # -a app / -e env / -t tag
    # --app=app / --env=env / --tag=tag

    try:
        opts, _ = getopt.getopt(
            sys.argv[1:],
            'e:',
            ['env=']
        )
    except getopt.GetoptError as e:
        raise e
    t = {
        'env': '',
    }

    for idx, arg in enumerate(sys.argv):
        if arg == '-env':
            val = sys.argv[idx + 1]
            if val and not val.startswith('-'):
                t['env'] = val

        if arg.startswith('-env'):
            arr = arg.split('=')
            if arr and len(arr) == 2:
                t['env'] = arr[1]

    print(f"Start commond options: {t}")

    return t


def load_cfg(env: str):
    """
    load configs
    :param env:
    :return:
    """
    if not env:
        raise Exception('env not specified')
    cfg_dir = os.path.join('cfg', env)
    assert os.path.isdir(cfg_dir)

    # env file
    env_file = os.path.join(cfg_dir, 'app.cfg')
    print(f"Loading env file from: {env_file}")
    load_dotenv(dotenv_path=env_file)

    # logger cfg
    logger_cfg_file = os.path.join(cfg_dir, 'logger.json')
    print(f"Loading logger config from: {logger_cfg_file}")
    logger_cfg = json.loads(open(logger_cfg_file, encoding='utf-8').read())
    assert isinstance(logger_cfg, dict)

    return {
        'log_config': logger_cfg,
        'env_file': env_file,
    }


def init_config(env: str = None) -> Dict:
    _fix_dotenv()
    opts = get_cmd_opts()
    _env = env or opts['env']
    cfg = load_cfg(_env)
    cfg['env'] = _env

    return cfg


if __name__ == '__main__':
    # 初始化环境变量
    configs = init_config('dev')

    urls = [
        '6932063804469',
        '6923074087200',
        '6921489023813',
        '190781771289',
        '190781771265',
        '193905023509',
        '193905023516',
        '193905023523',
        '6974718012010',
        '6974718013185',
        '6974718013208',
        '6974718014090',
        '6935205374790',
        '718037858425',
        '6937436198930',
        '6941574711388',
        '6901586104233',
        '4901080955517',
        '6921489003266',
        '6937436198480',
        '6936743812201',
        '6950885598465',
        '6923074066014',
        '6923074066014',
        '6941574752800',
        '6902022132124',
        '6910019008635',
        '6902022133206',
        '4260608930987',
        '6902022138218',
        '6902022134517',
        '6902022131219',
        '6902022131073',
        '6902022130519',
        '6941463591657',
        '6971685141521',
        '6941113160691',
        '6921489035564',
        '6921489034628',
        '6974658081251',
        '6936486812919',
        '6917751430403',
        '6934290355066',
        '6917751461117',
        '6934290357657',
        '6941798431826',
        '6972391540714',
        '6930800511274',
        '6971544012214',
        '6971544011965',
        '6974718017435',
        '6931847172145',
        '6935225500018',
        '6956755255155',
        '6974718011976',
        '6974718019675',
        '6950885582655',
        '6974188850365',
        '6926385310562',
        '6937819463549',
        '6921734964922',
        '6921734965325',
        '6921734938589',
        '6969696969699',
        '6935205311627',
        '6972417144155',
        '6921734949004',
        '192018046443',
        '192018046429',
        '192018046429',
        '192018046450',
        '6910527018874',
        '6910527018867',
        '6910527020143',
        '6910527018867',
        '6910527023571',
        '6910527018874',
        '6910527023120',
        '6910527021805',
        '6910527023885',
        '6910527020143',
        '6910527023571',
        '6910527023885',
        '6954545521534',
        '6954545521541',
        '6935205357878',
        '6930800511274',
        '6935835904732',
        '6974718014786',
        '6974718019804',
        '6921734965325',
        '6971039691863',
        '6937942633871',
        '6958679606815',
    ]

    # 流彩接口
    from zcbot_crawl_core.publish import stream as stream_service
    from zcbot_crawl_core.model.stream import StreamApiData, StreamTaskItem

    api_data = StreamApiData()
    api_data.appCode = "aaaa"
    api_data.spiderIds = ["barcode_gds:barcode"]  # skuInfo
    task_items = []
    for url in urls:
        task_item = StreamTaskItem()
        task_item.sn = url
        task_item.platCode = "gds"
        task_item.callback = {'screenshot': True}
        task_items.append(task_item)
    api_data.taskItems = task_items
    rs = stream_service.publish(api_data)
    print(rs)
