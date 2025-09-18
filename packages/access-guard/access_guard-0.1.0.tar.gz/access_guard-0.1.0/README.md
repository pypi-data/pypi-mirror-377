Access Guard
============

一個極輕量的 runtime 防護工具，提供 `@final` 裝飾器與 `Access` metaclass，
阻止被標註為 final 的方法 / property 在子類中被覆寫，並防止類別建立後的動態覆寫。

特點
-----
- 支援普通方法、`@staticmethod`、`@classmethod`、`@property` (含 getter/setter/deleter)。
- 不依賴第三方套件，僅使用標準函式庫。
- 在類別建立階段即檢查，違規直接拋出 `RuntimeError`。
- 防止猴子補丁：類別建立後再次指派 final 成員也會被阻擋。

安裝
----
```bash
pip install access-guard
```

快速示例
--------
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

行為細節
--------
1. `@final` 會在實際函式物件上標記特殊屬性；對 property 會同時標記其 accessor。  
2. `Access` metaclass 在 `__new__` 中收集所有基類的 final 名稱並檢查是否違規覆寫。  
3. 類別建立後再次透過賦值覆寫 final 名稱會在 `__setattr__` 被拒絕。  
4. 目前不阻擋魔術方法 (如 `__init__`)，若要啟用可修改 `final.py` 中 `_collect_final_names_from_bases` 的條件。  

限制 / 注意事項
----------------
- 僅在 class 定義與動態賦值層級防護；不處理 instance 屬性。  
- 不追蹤別名引用 (你仍可複製函式物件再指派為其他名稱)。  
- 與多重繼承共用時，若多個基類定義不同成員名稱，照常運作；如果名稱衝突且某基類標為 final，子類不可覆寫。  

測試
----
安裝開發相依後執行：
```bash
pip install -e .[dev]
pytest -q
```

版本策略
--------
採語義化版本。初期階段 (<1.0.0) 可能進行破壞式調整。

授權
----
MIT License，詳見 `LICENSE`。

未來規劃
--------
- 提供 `final_class` 裝飾器，一次鎖定整個類別所有成員。  
- 增加型別註解與 mypy plugin (讓靜態分析工具也能偵測)。  
- CI 自動化與發佈工作流程。  

