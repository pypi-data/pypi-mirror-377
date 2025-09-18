(module
  (import "env" "print" (func $print (param f64)))
  (func $main
    f64.const 1
    call $print
    f64.const 2
    call $print
    f64.const 3
    call $print
  )
  (export "main" (func $main))
)
