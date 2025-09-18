import sys
import traceback


def error_info(show_details=False) -> str:
    exc_type, exc_value, exc_tb = sys.exc_info()
    line_number = traceback.extract_tb(exc_tb)[-1][1]  # 获取发生异常的行号
    error_info = str(exc_value)  # 获取异常信息
    
    if show_details:
        print("Error line: ", line_number)
        print("Error info: ", traceback.format_exc())
    return f"{line_number}: {error_info}"