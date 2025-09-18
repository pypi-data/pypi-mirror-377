Access Guard
============

一個極輕量的 runtime 防護工具，提供 `@final` 裝飾器、`final_class` 以及 `Access` metaclass，
阻止被標註為 final 的方法 / property / (可選) 魔術方法在子類中被覆寫，並防止類別建立後的動態覆寫。

特點
-----
- 支援普通方法、`@staticmethod`、`@classmethod`、`@property` (含 getter / setter / deleter)。
- 選擇性鎖定魔術方法：`@final_class(include_magic=True)`。
- 不依賴第三方套件，僅使用標準函式庫，零執行期外部相依。
- 在類別建立階段即檢查，違規直接拋出 `RuntimeError` (fail fast)。
- 防止猴子補丁 (monkey patch)：類別建立後再次指派 final 成員也會被阻擋。
- PEP 561：提供 `py.typed`，對使用者型別檢查友善。
- O(成員數) 的輕量掃描；不對執行中呼叫加額外開銷。

安裝
----

支援 Python 3.10+。

使用 uv：
```bash
uv add access-guard
```

或使用 pip：
```bash
pip install access-guard
```

快速示例  
--------
`final`

```python
from access_guard import Access, final

class Base(metaclass=Access):
	@final
	def stable(self):
		return "v1"

	@property
	@final
	def value(self):
		return 42

class Child(Base):
	pass

Child().stable()  # OK

# 下列行為任一種將觸發 RuntimeError：
# class Bad(Base):
#     def stable(self):  # 覆寫 final 方法
#         return "v2"

# Bad.stable = lambda self: "hack"   # 類別建立後動態覆寫
```

`final_class`

一次將類別內目前所有「非魔術」成員標記為 final：

```python
from access_guard import Access, final_class

@final_class
class Service(metaclass=Access):
	def create(self):
		return "created"

	def delete(self):
		return "deleted"

class Child(Service):
	pass  # OK

# 以下會失敗：
# class Bad(Service):
#     def create(self):  # RuntimeError
#         return "x"
```

注意：後續在類別建立後動態新增新成員不會自動成為 final；建議在定義完成時使用 (這些成員可再個別用 `@final` 標記)。

參數使用：

```python
from access_guard import Access, final_class

# 排除某些方法不鎖定
@final_class(exclude={"debug", "open"})
class Service(metaclass=Access):
	def create(self): ...  # final
	def debug(self): ...   # not final
	def open(self): ...    # not final

# 鎖定包含魔術方法
@final_class(include_magic=True)
class Model(metaclass=Access):
	def __repr__(self):
		return "Model()"  # final
	def run(self):
		return 1           # final

# 同時使用
@final_class(exclude=["__repr__"], include_magic=True)
class Partial(metaclass=Access):
	def __repr__(self):  # not final
		return "P()"
	def calc(self):      # final
		return 42
```

參數說明：
- `exclude`: iterable[str]，列出不標記 final 的名稱，可用 list / set / tuple。  
- `include_magic`: True 時，會連 `__repr__` 這類魔術方法一起標記（永遠忽略內建底層 `__dict__`, `__weakref__`）。  

行為細節
--------
1. `@final` 會在實際函式 / property / descriptor 物件上標記特殊屬性；對 property 會同時標記其 accessor。  
2. `final_class` 會在裝飾當下收集類內所有成員並標記；`exclude` 與 `include_magic` 控制範圍。  
3. `Access` metaclass 在 `__new__`：
	- 收集所有基類 final 名稱 (含魔術)；
	- 檢查子類是否覆寫；
	- 合併並記錄到子類。  
4. 類別建立後再次透過賦值覆寫 final 名稱會在 `__setattr__` 被拒絕。  
5. 若某基類用 `final_class(include_magic=True)`，其魔術方法會被鎖定並傳遞到所有子類。  

限制 / 注意事項
----------------
- 僅在 class 定義與動態賦值層級防護；不處理 instance 屬性。  
- 不追蹤別名引用 (你仍可複製函式物件再指派為其他名稱)。  
- 與多重繼承共用時：若多個基類定義不同成員名稱，照常運作；若名稱衝突且某基類標為 final，子類不可覆寫。  
- 不反射攔截 `types.FunctionType` 以外複雜 descriptor 的動態產生行為 (如某些動態 __getattr__ pattern)。  
- 不試圖阻擋 metaclass 層級直接操作 `__dict__` 的低階繞過 (刻意攻擊場景)。  

測試
----
安裝開發相依後執行：

```bash
uv sync --extra dev
uv run pytest -q
```

或使用 pip：
```bash
pip install -e .[dev]
pytest -q
```

版本策略
--------
採語義化版本（Semantic Versioning）。初期階段 (<1.0.0) 可能進行破壞式調整。
目前版本：0.1.3。

未來規劃（可能）：
- 增加針對 instance 資源鎖定的 opt-in 模式。
- 與型別檢查器 (mypy/pyright) 整合 plugin (靜態提前報警)。
- 提供 CLI quick scan (列出哪些名稱被鎖定)。
- 追蹤覆寫意圖：允許以 `@allow_override` 明確放行 (設計中)。

授權
----
MIT License，詳見 `LICENSE`。

回饋 / 貢獻
------------
歡迎發 Issue / PR：
- 描述使用情境與預期行為
- 提供最小可重現程式碼
- 指出 Python 版本與套件版本

若提效能議題，請附上簡易 benchmark (timeit 或 pyperf)。

