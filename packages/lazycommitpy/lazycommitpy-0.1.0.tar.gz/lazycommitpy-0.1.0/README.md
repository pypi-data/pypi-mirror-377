<div align="center">
  <div>
    <h1 align="center">lazycommitpy</h1>
<img width="2816" height="1536" alt="lazycommit" src="https://github.com/user-attachments/assets/ee0419ef-2461-4b45-8509-973f3bb0f55c" />

  </div>
	<p>A Python CLI that writes your git commit messages for you with AI using Groq. Never write a commit message again.</p>
	<a href="https://pypi.org/project/lazycommitpy/"><img src="https://img.shields.io/pypi/v/lazycommitpy" alt="Current version"></a>
	<a href="https://github.com/KartikLabhshetwar/lazycommitpy"><img src="https://img.shields.io/github/stars/KartikLabhshetwar/lazycommitpy" alt="GitHub stars"></a>
	<a href="https://github.com/KartikLabhshetwar/lazycommitpy/blob/main/LICENSE"><img src="https://img.shields.io/pypi/l/lazycommitpy" alt="License"></a>
</div>

---

## Setup

> The minimum supported version of Python is 3.9. Check your Python version with `python --version`.

1. Install _lazycommitpy_:

   ```sh
   pip install lazycommitpy
   ```

   Or using UV (recommended):

   ```sh
   uv pip install lazycommitpy
   ```

### Install from source

```sh
git clone https://github.com/KartikLabhshetwar/lazycommitpy.git
cd lazycommitpy
uv pip install -e .
```

2. Retrieve your API key from [Groq Console](https://console.groq.com/keys)

   > Note: If you haven't already, you'll have to create an account and get your API key.

3. Set the key so lazycommit can use it:

   ```sh
   lazycommit config set GROQ_API_KEY=<your token>
   ```

   This will create a `.lazycommit` file in your home directory.

### Upgrading

Check the installed version with:

```
lazycommit --version
```

If it's not the latest version, run:

```sh
pip install --upgrade lazycommitpy
```

Or with UV:

```sh
uv pip install --upgrade lazycommitpy
```

## Usage

### CLI mode

You can call `lazycommit` directly to generate a commit message for your staged changes:

```sh
git add <files...>
lazycommit
```

`lazycommit` passes down unknown flags to `git commit`, so you can pass in [`commit` flags](https://git-scm.com/docs/git-commit).

For example, you can stage all changes in tracked files as you commit:

```sh
lazycommit --all # or -a
```

> 👉 **Tip:** Use the `lzc` alias if `lazycommit` is too long for you.

#### Generate multiple recommendations

Sometimes the recommended commit message isn't the best so you want it to generate a few to pick from. You can generate multiple commit messages at once by passing in the `--generate <i>` flag, where 'i' is the number of generated messages:

```sh
lazycommit --generate <i> # or -g <i>
```

> Warning: this uses more tokens, meaning it costs more.

#### Generating Conventional Commits

If you'd like to generate [Conventional Commits](https://conventionalcommits.org/), you can use the `--type` flag followed by `conventional`. This will prompt `lazycommit` to format the commit message according to the Conventional Commits specification:

```sh
lazycommit --type conventional # or -t conventional
```

This feature can be useful if your project follows the Conventional Commits standard or if you're using tools that rely on this commit format.

#### Exclude files from analysis

You can exclude specific files from AI analysis using the `--exclude` flag:

```sh
lazycommit --exclude package-lock.json --exclude dist/
```

#### Handling large diffs

For large commits with many files, lazycommit automatically stays within API limits:

- **Automatic detection**: Large diffs are detected
- **Per-file splitting**: Diffs are split by file first
- **Safe chunking**: Each file diff is chunked conservatively (default: 4000 tokens)
- **Smart combination**: Results are combined into one concise message
- **Fallback summaries**: For very large changes, uses compact summaries

### Git hook

You can also integrate _lazycommit_ with Git via the [`prepare-commit-msg`](https://git-scm.com/docs/githooks#_prepare_commit_msg) hook. This lets you use Git like you normally would, and edit the commit message before committing.

#### Install

In the Git repository you want to install the hook in:

```sh
lazycommit hook install
```

#### Uninstall

In the Git repository you want to uninstall the hook from:

```sh
lazycommit hook uninstall
```

#### Usage

1. Stage your files and commit:

   ```sh
   git add <files...>
   git commit # Only generates a message when it's not passed in
   ```

   > If you ever want to write your own message instead of generating one, you can simply pass one in: `git commit -m "My message"`

2. Lazycommit will generate the commit message for you and pass it back to Git. Git will open it with the [configured editor](https://docs.github.com/en/get-started/getting-started-with-git/associating-text-editors-with-git) for you to review/edit it.

3. Save and close the editor to commit!

## Configuration

### Reading a configuration value

To retrieve a configuration option, use the command:

```sh
lazycommit config get <key>
```

For example, to retrieve the API key, you can use:

```sh
lazycommit config get GROQ_API_KEY
```

You can also retrieve multiple configuration options at once by separating them with spaces:

```sh
lazycommit config get GROQ_API_KEY generate
```

### Setting a configuration value

To set a configuration option, use the command:

```sh
lazycommit config set <key>=<value>
```

For example, to set the API key, you can use:

```sh
lazycommit config set GROQ_API_KEY=<your-api-key>
```

You can also set multiple configuration options at once by separating them with spaces, like

```sh
lazycommit config set GROQ_API_KEY=<your-api-key> generate=3 locale=en
```

### Options

#### GROQ_API_KEY

Required

The Groq API key. You can retrieve it from [Groq Console](https://console.groq.com/keys).

#### locale

Default: `en`

The locale to use for the generated commit messages. Consult the list of codes in: https://wikipedia.org/wiki/List_of_ISO_639-1_codes.

#### generate

Default: `1`

The number of commit messages to generate to pick from.

Note, this will use more tokens as it generates more results.

#### proxy

Set a HTTP/HTTPS proxy to use for requests.

To clear the proxy option, you can use the command (note the empty value after the equals sign):

```sh
lazycommit config set proxy=
```

#### model

Default: `openai/gpt-oss-120b`

#### timeout

The timeout for network requests to the Groq API in milliseconds.

Default: `10000` (10 seconds)

```sh
lazycommit config set timeout=20000 # 20s
```

#### max-length

The maximum character length of the generated commit message.

Default: `50`

```sh
lazycommit config set max-length=100
```

#### type

Default: `""` (Empty string)

The type of commit message to generate. Set this to "conventional" to generate commit messages that follow the Conventional Commits specification:

```sh
lazycommit config set type=conventional
```

You can clear this option by setting it to an empty string:

```sh
lazycommit config set type=
```

#### chunk-size

Default: `4000`

The maximum number of tokens per chunk when processing large diffs. This helps avoid API limits and keeps requests fast:

```sh
lazycommit config set chunk-size=4000
```

**Note**: Must be between 1000-8000 tokens (Groq API limit).

## How it works

This CLI tool runs `git diff` to grab all your latest code changes, sends them to Groq's AI models, then returns the AI generated commit message.

The tool uses Groq's fast inference API to provide quick and accurate commit message suggestions based on your code changes.

### Large diff handling

For large commits that exceed API token limits, lazycommit automatically:

1. **Splits by file** to avoid oversized requests
2. **Chunks each file** into manageable pieces (default: 4000 tokens)
3. **Processes chunks** and combines results into a single message
4. **Falls back gracefully** to compact summaries for very large changes
5. **Smart merging** combines multiple chunk results intelligently

This ensures you can commit large changes (like new features, refactoring, or initial project setup) without hitting API limits.

## Troubleshooting

### "Request too large" error (413)

If you get a 413 error, your diff is too large for the API. Try these solutions:

1. **Exclude build artifacts**:
   ```sh
   lazycommit --exclude "dist/**" --exclude "__pycache__/**" --exclude ".pytest_cache/**"
   ```

2. **Reduce chunk size**:
   ```sh
   lazycommit config set chunk-size=3000
   ```

3. **Use a different model**:
   ```sh
   lazycommit config set model=llama-3.1-70b-versatile
   ```

4. **Commit in smaller batches**:
   ```sh
   git add src/  # Stage only source files
   lazycommit
   git add docs/ # Then stage documentation
   lazycommit
   ```

### No commit messages generated

- Check your API key: `lazycommit config get GROQ_API_KEY`
- Verify you have staged changes: `git status`
- Try reducing chunk size or excluding large files

### Slow performance with large diffs

- Reduce chunk size: `lazycommit config set chunk-size=3000`
- Exclude unnecessary files: `lazycommit --exclude "*.log" --exclude "*.tmp"`

### Installation issues

If you encounter issues installing with pip, try:

```sh
# Use UV (recommended)
pip install uv
uv pip install lazycommitpy

# Or upgrade pip first
pip install --upgrade pip
pip install lazycommitpy
```

## Python Features

This Python implementation includes several enhancements over the Node.js version:

- **Rich Console UI**: Beautiful terminal output with progress indicators
- **Enhanced Error Handling**: Detailed error messages with helpful suggestions  
- **Smart Configuration**: Robust config validation with clear error messages
- **Cross-platform Hooks**: Works seamlessly on Windows, macOS, and Linux
- **UV Support**: Optimized for modern Python package management with UV

## Why Groq?

- **Fast**: Groq provides ultra-fast inference speeds
- **Cost-effective**: More affordable than traditional AI APIs
- **Open source models**: Uses leading open-source language models
- **Reliable**: High uptime and consistent performance

## Requirements

- Python 3.9 or higher
- Git (for repository operations)
- Internet connection (for Groq API)

## Dependencies

- `typer`: Modern CLI framework
- `groq`: Official Groq Python client
- `rich`: Beautiful terminal formatting

## Maintainers

- **Kartik Labhshetwar**: [@KartikLabhshetwar](https://github.com/KartikLabhshetwar)

## License

This project is licensed under the Apache-2.0 License - see the [LICENSE](LICENSE) file for details.