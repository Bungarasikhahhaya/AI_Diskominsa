import inspect, importlib
mod = importlib.import_module('langchain_google_genai')
print('module', mod.__file__)
for name in ['ChatGoogleGenerativeAI', 'GoogleGenerativeAI', 'GoogleGenerativeAIEmbeddings']:
    obj = getattr(mod, name, None)
    print('\n===', name, '===')
    if obj is None:
        print('NOT FOUND')
    else:
        try:
            print(inspect.signature(obj))
        except Exception as e:
            print('signature error', e)
        try:
            src = inspect.getsource(obj)
            print(src[:1200])
        except Exception as e:
            print('source error', e)
