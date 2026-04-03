#ifndef PYTRA_BUILT_IN_PY_RUNTIME_H
#define PYTRA_BUILT_IN_PY_RUNTIME_H

// py_runtime.h — compatibility facade.
// New code should include individual headers directly.

#include "core/py_types.h"
#include "core/exceptions.h"
#include "core/io.h"
#include "built_in/base_ops.h"
#include "core/str_methods.h"
#include "core/conversions.h"
#include "built_in/list_ops.h"
#include "built_in/dict_ops.h"
#include "built_in/set_ops.h"
#include "built_in/bounds.h"
#include "core/tagged_value.h"
#include "core/rc_ops.h"
#include "core/scope_exit.h"
#include "../built_in/contains.h"
#include "../built_in/io_ops.h"
#include "../built_in/scalar_ops.h"
#include "../built_in/iter_ops.h"
#include "../built_in/sequence.h"

// NOTE: built_in/string_ops.h と built_in/type_id.h は runtime/east/ から
// emit パイプラインで生成されるヘッダー。ソースツリーには存在しない。
// emitter が必要に応じて個別に include を生成する。
// py_runtime.h からは include しない。

// py_div / py_floordiv / py_mod は built_in/scalar_ops.h へ移動済み。

#endif  // PYTRA_BUILT_IN_PY_RUNTIME_H
