<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Good example: input-validation.no-shell-injection no shell injection from user input

Substrate-original good patterns. Adapt to your stack.

## Pattern A: Python subprocess with argument list

```python
import subprocess

def convert_image(input_path: str, output_path: str) -> bool:
    # Argument list invocation; no shell parsing.
    # shell=False is the default; stated explicitly for clarity.
    result = subprocess.run(
        ["/usr/bin/convert", input_path, "-resize", "800x600", output_path],
        shell=False,
        timeout=30,
        check=False,
    )
    return result.returncode == 0
```

The arguments pass as a list; the operating system's exec
syscall receives a fixed argv array. Special characters in the
input path are treated as literal characters, not as shell
metacharacters.

## Pattern B: Node.js child_process.execFile

```javascript
const { execFile } = require('child_process');
const { promisify } = require('util');
const execFileAsync = promisify(execFile);

async function convertImage(inputPath, outputPath) {
  try {
    await execFileAsync(
      '/usr/bin/convert',
      [inputPath, '-resize', '800x600', outputPath],
      { timeout: 30000 }
    );
    return true;
  } catch (err) {
    return false;
  }
}
```

execFile invokes the binary directly; no shell is involved.

## Pattern C: Java ProcessBuilder

```java
public boolean convertImage(String inputPath, String outputPath) {
    ProcessBuilder pb = new ProcessBuilder(
        "/usr/bin/convert", inputPath, "-resize", "800x600", outputPath
    );
    pb.redirectErrorStream(true);
    try {
        Process p = pb.start();
        boolean finished = p.waitFor(30, TimeUnit.SECONDS);
        return finished && p.exitValue() == 0;
    } catch (IOException | InterruptedException e) {
        return false;
    }
}
```

ProcessBuilder with a List of strings; the JVM's process API
does not invoke a shell.

## Pattern D: Go exec.Command

```go
func ConvertImage(ctx context.Context, inputPath, outputPath string) error {
    ctx, cancel := context.WithTimeout(ctx, 30*time.Second)
    defer cancel()
    cmd := exec.CommandContext(ctx,
        "/usr/bin/convert",
        inputPath, "-resize", "800x600", outputPath,
    )
    return cmd.Run()
}
```

exec.Command takes the command and variadic arguments; no shell.

## Pattern E: Command allowlist when command is dynamic

```python
ALLOWED_COMMANDS = {
    "ls": "/bin/ls",
    "stat": "/usr/bin/stat",
    "file": "/usr/bin/file",
}

def run_inspection(command: str, target_path: str) -> str:
    binary = ALLOWED_COMMANDS.get(command)
    if binary is None:
        raise ValueError(f"command not permitted: {command}")
    result = subprocess.run(
        [binary, target_path],
        shell=False,
        capture_output=True,
        text=True,
        timeout=10,
    )
    return result.stdout
```

When the command itself is user-influenced, the substrate-
recommended pattern allowlists the permitted commands and looks
up the absolute binary path from the allowlist.
