<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Anti-example: input-validation.no-shell-injection no shell injection from user input (forbidden patterns)

Substrate-original anti-patterns. Do not copy into production.

## Anti-pattern A: shell=True with f-string (Python)

```python
import subprocess

# FORBIDDEN: shell=True interprets the string through /bin/sh.
# An attacker submits filename="x.jpg; rm -rf /" and gains RCE.
def convert_image_BAD(filename):
    subprocess.run(
        f"convert {filename} -resize 800x600 /tmp/out.jpg",
        shell=True,
    )
```

Why this violates input-validation.no-shell-injection:
- shell=True invokes /bin/sh on the command string
- f-string substitution lets the user inject shell metacharacters
- The semicolon ends the convert command; rm -rf executes next
- This is canonical CWE-78 OS command injection

## Anti-pattern B: os.system with concatenation (Python)

```python
import os

# FORBIDDEN: os.system always runs through the shell.
def run_check_BAD(host):
    os.system("ping -c 1 " + host)
```

## Anti-pattern C: child_process.exec with template literal (Node.js)

```javascript
const { exec } = require('child_process');

// FORBIDDEN: exec spawns a shell to interpret the command.
function convertImageBAD(filename) {
  exec(`convert ${filename} -resize 800x600 /tmp/out.jpg`, (err, stdout) => {
    console.log(stdout);
  });
}
```

## Anti-pattern D: Runtime.exec with single string (Java)

```java
// FORBIDDEN: Runtime.exec with a single string argument splits
// on whitespace and runs through the JVM's process API in a
// way that exposes shell-like injection on some platforms.
public void convertImageBAD(String filename) throws IOException {
    Runtime.getRuntime().exec(
        "/usr/bin/convert " + filename + " -resize 800x600 /tmp/out.jpg"
    );
}
```

## Anti-pattern E: Kernel.system single-string form (Ruby)

```ruby
# FORBIDDEN: system with a single string goes through /bin/sh
# when metacharacters are present.
def convert_image_BAD(filename)
  system("convert #{filename} -resize 800x600 /tmp/out.jpg")
end
```

## Anti-pattern F: Go shell wrapper

```go
// FORBIDDEN: Go has no exec-via-shell by default, so this
// pattern goes out of its way to invoke /bin/sh.
func ConvertImageBAD(filename string) error {
    cmd := exec.Command("/bin/sh", "-c",
        fmt.Sprintf("convert %s -resize 800x600 /tmp/out.jpg", filename))
    return cmd.Run()
}
```

## Anti-pattern G: PHP exec with concatenation

```php
<?php
// FORBIDDEN: exec passes the string to /bin/sh on Linux.
function convertImageBAD($filename) {
    exec("convert " . $filename . " -resize 800x600 /tmp/out.jpg");
}
?>
```

## Why mechanical detection fires on all of these

Semgrep registry rules detect:
- shell=True with non-constant string
- os.system, os.popen with any user input
- child_process.exec with template literal or concatenation
- Runtime.exec single-string variant with concatenation
- Kernel.system with string interpolation
- exec.Command wrapping /bin/sh -c with user input
- PHP exec / system / passthru / shell_exec call sites

All patterns map to CWE-78 / CWE-77.
