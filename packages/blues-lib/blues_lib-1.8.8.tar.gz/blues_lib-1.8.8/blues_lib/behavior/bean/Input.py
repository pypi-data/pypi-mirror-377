import sys,os,re,time
from typing import Any
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from behavior.bean.Bean import Bean

class Input(Bean):

  _keys = ['target_CS_WE','value','parent_CS_WE','timeout']

  def _set(self)->Any:
    granularity = self._config.get('granularity','text')
    if granularity=='char':
      return self._input_by_char()
    elif granularity=='discontinuous':
      return self._input_discontinuous()
    else:
      return self._input_by_text()
    
  def _input_discontinuous(self):
    kwargs = self._get_kwargs(self._keys)
    min = self._config.get('min',0.02)
    max = self._config.get('max',0.1)
    kwargs = {**kwargs,'min':min,'max':max}
    return self._browser.element.input.write_discontinuous(**kwargs)

  def _input_by_text(self)->Any:
    kwargs = self._get_kwargs(self._keys)
    self._input_by_mode(kwargs)

  def _input_by_char(self)->Any:
    interval = self._config.get('interval',0.5)
    value = self._config.get('value','') 
    # 这里必须重新选择元素，应对豆包登录，输入一个字符后元素重新绘制问题
    for char in str(value):
      time.sleep(interval)
      config = {
        'value':char
      }
      kwargs = self._get_kwargs(self._keys,config)

      self._input_by_mode(kwargs)

  def _input_by_mode(self,kwargs:dict)->Any:
    mode = self._config.get('mode','append')
    if mode=='replace':
      return self._browser.element.input.write(**kwargs)
    else:
      return self._browser.element.input.append(**kwargs)