import logging
import os

def get_logger(name: str, level=logging.DEBUG) -> logging.Logger:
    """
    获取一个配置好的 Logger，支持文件和控制台输出
    
    :param name: Logger 的名字
    :param log_file: 日志输出的文件路径（如果为 None，则不输出到文件）
    :param level: 设置日志的最低级别
    :return: 配置好的 Logger 实例
    """
    # 创建一个 Logger 实例
    logger = logging.getLogger(name)
    
    # 如果 Logger 已经被配置过（避免重复配置处理器）
    if logger.hasHandlers():
        return logger

    # 设置日志级别
    logger.setLevel(level)
    
    # 创建日志格式
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # 创建控制台处理器并设置格式
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 创建文件处理器
    file_handler = logging.FileHandler(os.path.join(os.getcwd(), "log.log"))
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


if __name__ == '__main__':
    # 使用示例
    logger = get_logger("MyGlobalLogger")
    logger.info("This is an info message.")
    logger.error("This is an error message.")
