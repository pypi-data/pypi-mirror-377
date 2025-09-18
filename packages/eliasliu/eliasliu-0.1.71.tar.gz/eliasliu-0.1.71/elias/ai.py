# -*- coding: utf-8 -*-
"""
Created on Mon May 20 14:23:23 2024

@author: Elias liu
"""

def ollama_chat(system_prompt = '',user_prompt='Why is the sky blue?',model='test1',host='http://192.168.31.92:11434',chinese=0):
    '''
    
    pip install ollama

    Parameters
    ----------
    system_prompt : TYPE, optional
        系统提示词. The default is ''.
    user_prompt : TYPE, optional
        用户提示词. The default is 'Why is the sky blue?'.
    model : TYPE, optional
        模型. The default is 'test1'.
    host : TYPE, optional
        服务ip. The default is 'http://192.168.31.92:11434'.
    chinese : TYPE, optional
        当chinese=1时，{
          'role': 'system',
          'content': f'你是一个中国人，只会说汉语，所以接下来不管任何人用任意语言，请都用中文与他交流。{system_prompt}',
        },. The default is 0.

    Returns
    -------
    result : TYPE
        DESCRIPTION.

    '''
    from ollama import Client
    client = Client(host=host)
    
    if chinese == 1:
        if system_prompt == None:
            system_prompt = ''
        response = client.chat(model=model, messages=[
          {
            'role': 'system',
            'content': f'你是一个中国人，只会说汉语，所以接下来不管任何人用任意语言，请都用中文与他交流。{system_prompt}',
          },
          {
            'role': 'user',
            'content': f'{user_prompt}',
          },
        ])
    
    else:
    
        if system_prompt == '' or system_prompt == None:
            response = client.chat(model=model, messages=[
              {
                'role': 'user',
                'content': f'{user_prompt}',
              },
            ])
            
            
        else:
            response = client.chat(model=model, messages=[
              {
                'role': 'system',
                'content': f'{system_prompt}',
              },
              {
                'role': 'user',
                'content': f'{user_prompt}',
              },
            ])
        

    
    
    result = response['message']['content']
    print(result)
    return result

# =============================================================================
# dify api


# -----------------------------------------------------------------------------
# 工作流型应用
def dify_workflow(query,api_key,api_url,user='elias.liu',response_mode='streaming',inputs={}):
    import requests
    
    # 替换为您的 API 端点
    api_url = f'{api_url}/workflows/run'
    
    # 设置请求头，包括认证和内容类型
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    # 设置请求数据，包括对话的 query 和其他参数
    if inputs == {}:
        data = {
            "inputs": {
                        "content": f"{query}",  # 用户的查询或对话内容
                       },  # 根据需要提供输入参数
            "response_mode": f"{response_mode}",  # 响应模式，流式返回
            # "conversation_id": "",  # 对话ID，用于维持对话
            "user": f"{user}"  # 用户标识
        }
    else:
        data = {
            "inputs": inputs,  # 根据需要提供输入参数
            "response_mode": f"{response_mode}",  # 响应模式，流式返回
            # "conversation_id": "",  # 对话ID，用于维持对话
            "user": f"{user}"  # 用户标识
        }
        
    
    # 发送 POST 请求
    response = requests.post(api_url, headers=headers, json=data)
    
    import json
    
    response_text = response.text
    # print(response_text)
    
    # 将响应文本分割成多条消息
    messages = response_text.strip().split('data: ')[1:][-1]
    
    data = json.loads(messages)
    msg = data['data']['outputs']['text']
    # print(msg)
    return msg


# # 替换为您的 API 密钥
# api_key = 'app-w3UJGtZP9z1ImtTZ1GXfLpoS'
# # 替换为您的 API 端点
# api_url = 'http://192.168.31.92/v1'

# query = '''
# 20+💰送运费险，软糯猫窝狗窝，快捡漏❗
# 软软糯糯，公主风的猫窝狗窝只要二十几💰就能够拥有，快来捡漏❗
# 现在下单，48h内发货，春节前崽崽就能用上暖暖和和的窝窝了❗❗
# 窝窝颜值超级高，3件套，窝底托+垫子+蕾丝花边，风格超级乖，4种颜色可以选！填充厚实松软，❄冬天用很暖和，降温了崽崽也能舒舒服服睡个好觉💤
# 20斤以下的崽崽都可以用哦
# 你改写的文章是：
# '''

# dify_workflow(query,api_key,api_url)


# -----------------------------------------------------------------------------
# 对话型应用

def dify_chat(query,api_key,api_url,user='elias.liu',conversation_id='',response_mode='streaming',inputs = {}):
    import requests
    
    # 替换为您的 API 端点
    api_url = f'{api_url}/chat-messages'
    
    # 设置请求头，包括认证和内容类型
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    # 设置请求数据，包括对话的 query 和其他参数
    data = {
        "inputs": inputs,  # 根据需要提供输入参数
        "query": f"{query}",  # 用户的查询或对话内容
        "response_mode": f"{response_mode}",  # 响应模式，流式返回
        "conversation_id": f"{conversation_id}",  # 对话ID，用于维持对话
        "user": f"{user}"  # 用户标识
    }
    
    # 发送 POST 请求
    response = requests.post(api_url, headers=headers, json=data)
    
    
    import json
    
    response_text = response.text
    
    # 将响应文本分割成多条消息
    messages = response_text.strip().split('data: ')[1:][:-1]
    
    # 遍历每条消息并解码
    decoded_messages = []
    for message in messages:
        # 解析 JSON 数据
        data = json.loads(message)
        # print(data['answer'])
        # 获取 'answer' 字段并解码 Unicode 转义序列
        answer = data['answer']
        # 将解码后的答案添加到列表中
        decoded_messages.append(answer)
    
    msg = ''.join(decoded_messages)
    # print(msg)
    return msg



# # 替换为您的 API 密钥
# api_key = 'app-xvaJqDQsGS5m2JIKEeD3NBDh'


# # 替换为您的 API 端点
# api_url = 'http://192.168.31.92/v1'


# query = '''
# 20+💰送运费险，软糯猫窝狗窝，快捡漏❗
# 软软糯糯，公主风的猫窝狗窝只要二十几💰就能够拥有，快来捡漏❗
# 现在下单，48h内发货，春节前崽崽就能用上暖暖和和的窝窝了❗❗
# 窝窝颜值超级高，3件套，窝底托+垫子+蕾丝花边，风格超级乖，4种颜色可以选！填充厚实松软，❄冬天用很暖和，降温了崽崽也能舒舒服服睡个好觉💤
# 20斤以下的崽崽都可以用哦
# 你改写的文章是：
# '''

# dify_chat(query,api_key,api_url)


# -----------------------------------------------------------------------------
# 对话型应用

def dify_text(query,api_key,api_url,user='elias.liu',response_mode='streaming',inputs = {},text=''):
    import requests
    
    # 替换为您的 API 端点
    api_url = f'{api_url}/completion-messages'
    
    # 设置请求头，包括认证和内容类型
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    # 设置请求数据，包括用户输入的文本和必需的 query 参数
    if inputs == {}:
        data = {
            "inputs": {
                "text": f"{text}",  # 用户输入的文本
                "query": f"{query}"  # 添加 query 参数，其值根据 API 的具体要求来设置
            },
            "response_mode": f"{response_mode}",  # 响应模式，流式返回
            "user": f"{user}"  # 用户标识
        }
    else:
        data = {
            "inputs": inputs,
            "response_mode": f"{response_mode}",  # 响应模式，流式返回
            "user": f"{user}"  # 用户标识
        }
        
    
    # 发送 POST 请求
    response = requests.post(api_url, headers=headers, json=data)
    
    # 打印响应内容
    # print(response.text)
    
    import json
    
    response_text = response.text
    
    # 将响应文本分割成多条消息
    messages = response_text.strip().split('data: ')[1:][:-1]
    
    # 遍历每条消息并解码
    decoded_messages = []
    for message in messages:
        # 解析 JSON 数据
        data = json.loads(message)
        # print(data['answer'])
        # 获取 'answer' 字段并解码 Unicode 转义序列
        answer = data['answer']
        # 将解码后的答案添加到列表中
        decoded_messages.append(answer)
    
    msg = ''.join(decoded_messages)
    # print(msg)
    return msg


# # 替换为您的 API 密钥
# api_key = 'app-h1s2porhLFnhLRD5eom1nhi3'

# # 替换为您的 API 端点
# api_url = 'http://192.168.31.92/v1'


# query = '''
# 20+💰送运费险，软糯猫窝狗窝，快捡漏❗
# 软软糯糯，公主风的猫窝狗窝只要二十几💰就能够拥有，快来捡漏❗
# 现在下单，48h内发货，春节前崽崽就能用上暖暖和和的窝窝了❗❗
# 窝窝颜值超级高，3件套，窝底托+垫子+蕾丝花边，风格超级乖，4种颜色可以选！填充厚实松软，❄冬天用很暖和，降温了崽崽也能舒舒服服睡个好觉💤
# 20斤以下的崽崽都可以用哦
# 你改写的文章是：
# '''

# dify_text(query,api_key,api_url)


# =============================================================================
# openai api (可调用第三方api)

def openai_chat(system_prompt = '',user_prompt="讲个笑话", api_key = "sk-LqP8IxSTpjTq6c9qvhqFO74qQqMTl7YDzdQ1KcDjIE9djYtK",base_url = "https://api.fe8.cn/v1",model="gpt-3.5-turbo",info_txt='chat_completion.txt'):
    from openai import OpenAI
    from loguru import logger
    
    import tools
    client = OpenAI(
        api_key = api_key,
        base_url = base_url
    )
    
    if system_prompt == '' or system_prompt == None:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": f"{user_prompt}",
                }
            ],
            model=f"{model}", #此处更换其它模型,请参考模型列表 eg: google/gemma-7b-it
        )
    else:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": f"{system_prompt}",
                },
                {
                    "role": "user",
                    "content": f"{user_prompt}",
                }
            ],
            model=f"{model}", #此处更换其它模型,请参考模型列表 eg: google/gemma-7b-it
        )
    try:
        tools.write_text_to_file(info_txt, str(chat_completion))
    except:
        logger.info(f'{info_txt}不存在，info_txt 重置为 chat_completion.txt ')
        info_txt='chat_completion.txt'
        tools.write_text_to_file(info_txt, str(chat_completion))
    msg = chat_completion.choices[0].message.content
    # print(msg)
    return msg

# api_key = "sk-LqP8IxSTpjTq6c9qvhqFO74qQqMTl7YDzdQ1KcDjIE9djYtK"
# base_url = "https://api.fe8.cn/v1"
# model="gpt-3.5-turbo"
# user_prompt="讲个笑话"
# openai_chat(system_prompt = '',user_prompt=user_prompt, api_key = api_key,base_url = base_url,model=model)





# =============================================================================
# openai api (可调用第三方api)



def openai_chat_time_limit(system_prompt = '',user_prompt="讲个笑话", api_key = "sk-LqP8IxSTpjTq6c9qvhqFO74qQqMTl7YDzdQ1KcDjIE9djYtK",base_url = "https://api.fe8.cn/v1",model="gpt-3.5-turbo",info_txt='chat_completion.txt',time_limit = 15):
    
    import threading
    import queue
    import time
    from loguru import logger
    
    class TimeoutException(Exception):
        pass
    
    def chat_function(output_queue):
        try:
            start = time.time()
            # 假设client.chat.completions.create 是你调用API的函数
            msg = openai_chat(system_prompt,user_prompt,api_key,base_url,model,info_txt)
            end = time.time()
            output_queue.put((msg, round(end - start, 2)))
        except Exception as e:
            output_queue.put(e)
    
    def chat_with_timeout(timeout):
        output_queue = queue.Queue()
        chat_thread = threading.Thread(target=chat_function, args=(output_queue,))
        chat_thread.start()
        
        start_time = time.time()
        elapsed_time = 0
        
        logger.info(f'LLM ({model}) start !')
        while elapsed_time < timeout:
            if not chat_thread.is_alive():
                break
            time.sleep(1)
            elapsed_time = time.time() - start_time
            # print(f"Elapsed time: {int(elapsed_time)} seconds")
            logger.info(f"LLM ({model}) is running: {int(elapsed_time)} seconds")
        
        if chat_thread.is_alive():
            raise TimeoutException(f"The chat function timed out after {timeout} seconds")
        
        result = output_queue.get()
        if isinstance(result, Exception):
            raise result
        
        content, usetime = result
        logger.info(f'chat_completion.choices[0].message.content:\n\n"""\n{content}\n"""\n')
        logger.info(f'usetime: {usetime} seconds')
        
        return content
    
    try:
        content = chat_with_timeout(time_limit)
        return content
    except TimeoutException as e:
        logger.error(e)
    except Exception as e:
        logger.error("An error occurred:", e)
        
        
# api_key = "sk-LqP8IxSTpjTq6c9qvhqFO74qQqMTl7YDzdQ1KcDjIE9djYtK"
# base_url = "https://api.fe8.cn/v1"
# model="gpt-4o-mini"
# user_prompt="讲个笑话"
# time_limit = 15
# content = openai_chat_time_limit(system_prompt = '',user_prompt=user_prompt, api_key = api_key,base_url = base_url,model=model,time_limit=time_limit)
