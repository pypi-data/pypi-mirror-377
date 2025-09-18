"""Runtime final guard decorators & metaclass."""

# --- 公用工具 ---

FINAL_ATTR = "__is_final__"

def _mark_func_final(func):
    # 在真正的 function 物件上標記
    setattr(func, FINAL_ATTR, True)

def _is_func_final(func):
    return getattr(func, FINAL_ATTR, False)

def final(obj):
    """
    將方法／屬性標註為 final。
    支援：普通函式、@staticmethod、@classmethod、@property（含 fget/fset/fdel）。
    """
    if isinstance(obj, staticmethod):
        _mark_func_final(obj.__func__)
        return staticmethod(obj.__func__)
    if isinstance(obj, classmethod):
        _mark_func_final(obj.__func__)
        return classmethod(obj.__func__)
    if isinstance(obj, property):
        # 任何一個 accessor 被標 final，都視為整個 property final
        if obj.fget:
            _mark_func_final(obj.fget)
        if obj.fset:
            _mark_func_final(obj.fset)
        if obj.fdel:
            _mark_func_final(obj.fdel)
        return obj
    # 一般函式
    _mark_func_final(obj)
    return obj


def final_class(_cls=None, *, exclude=None, include_magic=False):
    """將類別中方法 / property 批次標記為 final。

    可用法：
        @final_class
        class A: ...

        @final_class(exclude={"debug"}, include_magic=True)
        class B: ...

    參數:
        exclude: 可選 set/list/tuple，列出不標記 final 的成員名稱。
        include_magic: 若為 True，會連符合 __xxx__ 形式的魔術方法一併標記。
    """
    if exclude is None:
        exclude_set = set()
    else:
        exclude_set = set(exclude)

    def _apply(cls):
        magic_collected = set()
        for name, value in list(vars(cls).items()):
            is_magic = name.startswith("__") and name.endswith("__")
            if name in exclude_set:
                continue
            if is_magic and not include_magic:
                continue
            if is_magic and include_magic and name in {"__dict__", "__weakref__"}:
                # 這些內建結構不做處理
                continue
            # 標記
            if isinstance(value, (staticmethod, classmethod, property)):
                marked = final(value)
                setattr(cls, name, marked)
            elif callable(value):
                final(value)
            if is_magic and include_magic and _is_attr_final(getattr(cls, name)):
                magic_collected.add(name)
        # 更新 __final_names__ 若已存在
        if hasattr(cls, "__final_names__"):
            current = set(getattr(cls, "__final_names__"))
            newly = {
                n for n, v in vars(cls).items()
                if (include_magic or not (n.startswith("__") and n.endswith("__")))
                and n not in exclude_set
                and _is_attr_final(v)
            }
            setattr(cls, "__final_names__", frozenset(current | newly))
        if magic_collected:
            existing_magic = set(getattr(cls, "__final_magic_names__", frozenset()))
            setattr(cls, "__final_magic_names__", frozenset(existing_magic | magic_collected))
        return cls

    if _cls is not None and callable(_cls):  # 無參數使用情況
        return _apply(_cls)
    return _apply


def _is_attr_final(value):
    """判斷某個 class 層級的成員是否被標為 final。"""
    if isinstance(value, staticmethod) or isinstance(value, classmethod):
        return _is_func_final(value.__func__)
    if isinstance(value, property):
        return any(
            _is_func_final(f)
            for f in (value.fget, value.fset, value.fdel)
            if f is not None
        )
    # 其它可呼叫或可標記的描述元
    return _is_func_final(value)


def _collect_final_names_from_bases(bases):
    """蒐集所有基類中被標為 final 的成員名稱。

    - 一般方法/屬性：排除魔術 (除非該基類有 __final_magic_names__ 額外紀錄)。
    - 魔術方法：僅當祖先類別透過 final_class(include_magic=True) 記錄於 __final_magic_names__ 時才納入。
    """
    finals = set()
    magic_finals = set()
    for base in bases:
        # 僅看該層 __dict__，避免解析 descriptor 後的綁定結果
        for name, value in vars(base).items():
            if name.startswith("__") and name.endswith("__"):
                # 僅在祖先有顯式記錄時才視為最終
                if name in getattr(base, "__final_magic_names__", frozenset()) and _is_attr_final(value):
                    magic_finals.add(name)
                continue
            if _is_attr_final(value):
                finals.add(name)
        # 合併祖先已紀錄的魔術 final 名稱
        magic_finals.update(getattr(base, "__final_magic_names__", frozenset()))
    return finals | magic_finals


# --- Metaclass ---

class Access(type):
    """
    讓以 @final 標註的成員在子類中不可被覆寫，並阻擋建立後的動態覆蓋。
    """
    def __new__(mcs, name, bases, class_dict):
        # 1) 找出所有繼承鏈上的 final 名稱
        inherited_finals = _collect_final_names_from_bases(bases)

        # 2) 檢查本類是否嘗試覆寫這些名稱
        violated = inherited_finals.intersection(class_dict.keys())
        if violated:
            raise RuntimeError(
                f"下列成員已在父類標為 final，不可覆寫：{sorted(violated)}"
            )

        # 3) 建立類別
        cls = super().__new__(mcs, name, bases, class_dict)

        # 4) 保存「此類禁止覆寫的名稱集合」（包含祖先類）
        #    若本類也標了新的 final，下一代子類也會繼承。
        own_finals = {
            n for n, v in vars(cls).items()
            if not (n.startswith("__") and n.endswith("__")) and _is_attr_final(v)
        }
        # 合併所有來源
        all_finals = set(inherited_finals) | own_finals
        setattr(cls, "__final_names__", frozenset(all_finals))

        return cls

    def __setattr__(cls, name, value):
        """
        阻擋類別被建立後，再把 final 名稱重新賦值（猴補／動態覆寫）。
        """
        final_names = getattr(cls, "__final_names__", frozenset())
        if name in final_names:
            raise RuntimeError(f"成員 '{name}' 為 final，禁止重新賦值/覆寫。")
        return super().__setattr__(name, value)