#! /usr/bin/env python3
# -*- coding:utf-8 -*-
# @Time : 2025/01/13 18:35 
# @Author : JY
"""
系统相关的操作
"""

import concurrent.futures
import datetime
import json
import locale
import subprocess
import sys
import time


class sysHelper:

    @staticmethod
    def run_command(command, printInfo=True, returnStr=False, returnJson=False, encoding_utf8=False, encoding_gbk=False,
                    timeout=None):
        """
        :param command: 执行的命令
        :param printInfo: 是否打印info信息
        :param returnStr: 返回字符串 默认返回list
        :param returnJson: 返回json解析后的python可直接操作对象
        :param encoding_utf8:
        :param encoding_gbk:
        :param timeout: 超时时间 默认None不超时，可以设定一个秒数
        :return: 默认list 可选字符串和json解析后的对象
        """
        res_lines = []
        encoding = locale.getpreferredencoding(False)
        if encoding_utf8:
            encoding = 'utf-8'
        if encoding_gbk:
            encoding = 'gbk'
        if printInfo:
            print('info', 'run:', command)
        start_time = time.time()
        # 3.7以下的版本 text=True 报错，修改为universal_newlines=True
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True,
                                   universal_newlines=True,
                                   encoding=encoding)  # stderr=subprocess.PIPE,可以捕获错误，不设置就是直接输出
        printRes = False
        while True:
            if timeout is not None and time.time() - start_time > timeout:
                process.kill()
                print(sysHelper.red('Error'), sysHelper.red(f"Max allow {timeout} seconds, Time out!"))
                return None

            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                outStr = output.strip()
                res_lines.append(outStr)
                if printInfo:
                    if not printRes:
                        print('info', 'res:')
                        printRes = True
                    print(outStr)
                sys.stdout.flush()

        if returnStr:
            res_lines = '\n'.join(res_lines)
        if returnJson:
            res_lines = ''.join(res_lines)
            res_lines = json.loads(res_lines)
        exit_code = process.poll()
        if exit_code != 0:
            print(sysHelper.red('Error: '))
            for line in process.stderr:
                print(sysHelper.red(line.strip()))
            if isinstance(res_lines, list):
                for row in res_lines:
                    print(sysHelper.red(row))
            else:
                print(sysHelper.red(str(res_lines)))
            return None
        return res_lines

    @staticmethod
    def red(msg):
        """print以后会显示亮红色字体"""
        return f"\033[91m{msg}\033[0m"

    @staticmethod
    def green(msg):
        """print以后会显示亮绿色字体"""
        return f"\033[92m{msg}\033[0m"

    @staticmethod
    def display_all_colors():
        """
        显示全部可用的颜色
        :return:
        """
        j = 0
        for i in range(108):
            if i in [2, 3, 5, 6, 8, 38, 39, 48, 49, 50, 98] or 10 <= i <= 20 or 22 <= i <= 29 or 52 <= i <= 89:
                continue
            msg = f"\033[{i}m" + r"\033[%sm内容\033[0m" % i + "\033[0m"
            if i < 10:
                msg += " "
            if i < 100:
                msg += " "
            print(msg, '', '', end='')
            j += 1
            if j % 8 == 0:
                print()

    @staticmethod
    def logError(msg1='', msg2='', msg3=''):
        """1个参数默认就是红色，2个或者3个参数msg2是红色"""
        if msg2 == '' and msg3 == '':
            print(sysHelper.red(msg1))
        elif msg2 != '' and msg3 == '':
            print(msg1, sysHelper.red(msg2))
        elif msg2 != '' and msg3 != '':
            print(msg1, sysHelper.red(msg2), msg3)

    @staticmethod
    def logInfo(msg1='', msg2='', msg3=''):
        if msg2 == '' and msg3 == '':
            print(sysHelper.green(msg1))
        elif msg2 != '' and msg3 == '':
            print(msg1, sysHelper.green(msg2))
        elif msg2 != '' and msg3 != '':
            print(msg1, sysHelper.green(msg2), msg3)

    @staticmethod
    def input(prompt, not_empty=False, number_only=False, default_value=None, choice=None):
        """
        输入控制
        :param prompt: 显示给用户的提示
        :param not_empty: 不能为空
        :param number_only: 只能输入正整数
        :param default_value: 默认值
        :param choice: 只能从这里面选 可以是list 也可以是str str会默认循环
        :return: 输入
        """
        while True:
            if default_value is not None:
                if prompt.endswith(':'):
                    prompt = prompt[0:-1]
                prompt += "(Default=%s):" % default_value
            user_input = input(prompt).strip()
            if default_value is not None and not user_input:
                return default_value
            if not_empty and not user_input:
                print(sysHelper.red("输入无效,内容不能为空，请重新输入!"))
                continue
            if number_only and not user_input.isdigit():
                print(sysHelper.red("输入无效,内容只能是数字，请重新输入!"))
                continue
            if choice is not None:
                choice = [str(one_choice) for one_choice in choice]
                if user_input not in choice:
                    print(sysHelper.red(f"输入无效，请从 {choice} 中选择！"))
                    continue
            return user_input

    @staticmethod
    def run_tasks(task_func, task_params, max_workers=10, print_info=True, thread_mode=True, process_mode=False,
                  raise_exception=True, re_run_exception=0, last_run_info=None):
        """
            任务类型	     推荐方案	         核心原因
            IO 密集型	 多线程           线程切换开销小，IO 等待时释放 GIL     爬虫（等待网页响应）、API 调用（等待返回结果）、日志写入（磁盘 IO 等待）
            CPU 密集型	 多进程	         突破 GIL 限制，利用多核并行计算       大规模数据排序、矩阵运算、视频帧处理
        :param task_func: 方法对象
        :param task_params: 参数数组 例: [['a','b'],['a','c'],['b','d']]  或者 如果只有一个参数的话['a','b','c']
                            !!注意!! 参数列表中如果有部分参数是None,那么参数是None的那部分任务不会执行
        :param max_workers: 线程/进程 数量
        :param print_info: 打印执行信息
        :param thread_mode: 线程模式(默认)
        :param process_mode:进程模式
        :param raise_exception: 执行遇到异常是否抛出
        :param re_run_exception: 遇到异常任务的重跑次数,重跑完成后,再根据raise_exception的值决定是否抛出异常
                                !!注意!! 任务的成功失败,重跑与否,是看是否有异常抛出,而不是看任务的返回值
        :param last_run_info: 上次执行的结果,重跑异常的时候需要这个参数,主调用不需要传
        :return: success, results, exceptions
        """

        def empty_task(p):
            pass

        if process_mode:
            thread_mode = False
        process_or_thread_pool = None  # 线程或进程池
        if thread_mode:
            process_or_thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        if process_mode:
            process_or_thread_pool = concurrent.futures.ProcessPoolExecutor(max_workers=max_workers)
        # 对参数格式化
        task_params = [one if isinstance(one, list) else [one] for one in task_params]
        if print_info:
            print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '--->', "任务开始", task_func.__name__)
            print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '--->', "任务数量", task_params.__len__())
        with process_or_thread_pool as executor:
            futures = []
            for one_param in task_params:
                #  executor.submit(funcName, p1, p2,..)
                # 重跑到时候,为了使参数的index和原参数的index对齐,成功的参数用None代替,所以这里,当遇到None参数的时候,执行个空方法
                future = executor.submit(empty_task if len(one_param) == 1 and one_param[0] is None else task_func,
                                         *one_param)
                futures.append(future)

            # 监控线程池中剩余的任务数量
            all_futures = futures.__len__()
            while True:
                time.sleep(1)
                unfinished_count = sum(not future.done() for future in futures)
                if print_info:
                    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '--->',
                          f"完成进度: {all_futures - unfinished_count}/{all_futures}")
                if unfinished_count == 0:
                    break
            results = []
            exceptions = []
            index = 0
            for future in futures:
                if future.exception() is None:
                    results.append(future.result())
                    exceptions.append(None)
                else:
                    results.append(None)
                    exceptions.append(
                        datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " param_index:%s %s -> %s -> %s" % (
                            index, task_func.__name__ + '(' + str(task_params[index])[1:-1] + ')',
                            type(future.exception()).__name__, str(future.exception())))
                index += 1
            success = True if sum(0 if one is None else 1 for one in exceptions) == 0 else False

            # 合并上次和本次执行的结果
            if last_run_info is not None:
                success = success or last_run_info[0]
                results = [last_run_info[1][i] if last_run_info[1][i] is not None else results[i] for i in
                           range(len(results))]
                # exceptions默认就是最新的exceptions

            if raise_exception and not success and re_run_exception == 0:
                exception_str = "\n"
                for one in exceptions:
                    if one is not None:
                        exception_str += f"{one}\n"
                raise Exception(exception_str)
            if print_info:
                all_num = task_params.__len__()
                except_num = sum(0 if one is None else 1 for one in exceptions)
                success_num = all_num - except_num
                print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '--->', '执行完成', f"总数: {all_num}",
                      sysHelper.green(f"成功: {success_num}"), sysHelper.red(f"失败: {except_num}")  if except_num > 0 else sysHelper.green(f"失败: {except_num}"))
            if re_run_exception > 0 and not success:
                print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '--->', '开始重跑失败的任务',
                      f"当前执行完剩余{re_run_exception - 1}次")
                # 构建新的参数列表
                new_task_params = []
                index = 0
                for row in exceptions:
                    if row is None:
                        new_task_params.append(None)
                    else:
                        new_task_params.append(task_params[index])
                    index += 1
                """
                # 测试代码
                if re_run_exception == 4:
                    new_task_params = [
                        None,
                        [1, 1],
                        [1, 0],
                        None,
                    ]
                if re_run_exception <= 3:
                    new_task_params = [
                        None,
                        None,
                        [1, 1],
                        None,
                    ]
                """

                return sysHelper.run_tasks(task_func=task_func, task_params=new_task_params,
                                           max_workers=max_workers,
                                           print_info=print_info, thread_mode=thread_mode,
                                           process_mode=process_mode,
                                           raise_exception=raise_exception,
                                           re_run_exception=re_run_exception - 1,
                                           last_run_info=(success, results, exceptions))
            return success, results, exceptions


if __name__ == '__main__':
    pass
    # cmd = 'ping www.abaidu.com'
    # res = sysHelper.run_command(cmd,returnStr=True)
    # print('--------返回的结果---------')
    # print(res)
    # res = sysHelper.input('清输入：',not_empty=False,number_only=False,choice='12345')
    # res = sysHelper.input('清输入',not_empty=False,number_only=False,choice='yn',default_value='y')
    # print(res)

    # """
    params = [
        [1, 10],
        [1, 0],
        [1, 0],
        [1, 10],
    ]
    # params = [1,2,3,4,{'a':1}]
    res = sysHelper.run_tasks(task_func=lambda a, b: print(a / b), task_params=params, thread_mode=True, raise_exception=True,
                              re_run_exception=4)
    print('====================================================================')
    print(res)
    # """
