# CHANGELOG


## v2.0.0 (2024-11-28)

### :boom:

- :boom: Rename the logger instance to "pudly" and simplify imports
  ([`97783a1`](https://github.com/8-bit-hunters/pudly/commit/97783a1038c84001c97942dc7db9704b1eaef31e))

### :sparkles:

- :sparkles: Add basic HTTP authentication
  ([`44a378c`](https://github.com/8-bit-hunters/pudly/commit/44a378cdf6d8eca4569ebfb40b80a28cca281d9b))

### Other

- :pushpin: Run uv lock
  ([`115d997`](https://github.com/8-bit-hunters/pudly/commit/115d997e6457124df6eeb52c5bf0ba121e06b502))

- :construction_worker: Only build non-development parts in release build with frozen lock
  ([`a458ea1`](https://github.com/8-bit-hunters/pudly/commit/a458ea1c6d62ffae36ce2ed8be9a5b8cd5801b78))


## v1.0.0 (2024-11-23)

### :boom:

- :boom: Rename project to PUDLy
  ([`41e7301`](https://github.com/8-bit-hunters/pudly/commit/41e73010a01a928930c424dc848e8b2675df1a35))

- :boom: Indicate helper functions as private
  ([`19794cc`](https://github.com/8-bit-hunters/pudly/commit/19794cc089abf960f5db8460d5b6c2bcc38dd6ec))

### :sparkles:

- :sparkles: Add function to download multiple files concurrently
  ([`75fa5e1`](https://github.com/8-bit-hunters/pudly/commit/75fa5e188b58d4b995a1b9c09bd06d9682609904))

- :sparkles: Raise error if the downloaded file size doesn't match the total size
  ([`4368dce`](https://github.com/8-bit-hunters/pudly/commit/4368dcea054e5e387de6ce8921bcf171366319da))

- :sparkles: Return the path of the downloaded file
  ([`82c13e1`](https://github.com/8-bit-hunters/pudly/commit/82c13e167ca583e8977314f284034cadc2a2dc91))

- :sparkles: Add option to define download directory
  ([`8ab5483`](https://github.com/8-bit-hunters/pudly/commit/8ab54835bb93c7299f87a62ad18c62fab1301773))

- :sparkles: Allow to use query parameters
  ([`6fe9687`](https://github.com/8-bit-hunters/pudly/commit/6fe9687947475b4fb7974c0d2040ff46f0ee4cfe))

- :sparkles: Download file from a given URL
  ([`34d0427`](https://github.com/8-bit-hunters/pudly/commit/34d04274c7f9c46f6db9613cd11367b1a3889a8f))

### :zap:

- :zap: Increase the download chunk size to 25 MB
  ([`4ebac26`](https://github.com/8-bit-hunters/pudly/commit/4ebac26187e98303f0bc626168613177f77cdc11))

### Other

- :construction_worker: Use one workflow for releasing
  ([`0b5ba08`](https://github.com/8-bit-hunters/pudly/commit/0b5ba08e4023f66cb6c661dd3cafc39b2d5c3699))

- :green_heart: Fix publish trigger issue with PAT
  ([`5f9ff54`](https://github.com/8-bit-hunters/pudly/commit/5f9ff540628e5c26f79d08862d8d82618290f322))

- :construction_worker: Run PyPi publish also when release is published
  ([`549653e`](https://github.com/8-bit-hunters/pudly/commit/549653e205db44841c9cd780cf581f55edec7751))

- :construction_worker: Run PyPi publish when version tag is created
  ([`81314a2`](https://github.com/8-bit-hunters/pudly/commit/81314a24c0a49855c82ff92cb10efa488f43bc01))

- :memo: Fix testing Github workflow badge
  ([`7946b17`](https://github.com/8-bit-hunters/pudly/commit/7946b1776a207863a161c8807b7cec9d20d35edf))

- :construction_worker: Only publish to PyPi when release is created
  ([`4737f32`](https://github.com/8-bit-hunters/pudly/commit/4737f32329f4638600fe83bf3910212a05f9c8f4))

- :green_heart: Fix build failure
  ([`6f6bac5`](https://github.com/8-bit-hunters/pudly/commit/6f6bac52d934f441a2fb53e9805eda528ef87838))

- :construction_worker: Add publish link for PyPi
  ([`7f5c13c`](https://github.com/8-bit-hunters/pudly/commit/7f5c13ce54d5ffd7f889c81125cd5d35f2ce7c67))

- :memo: Add documentation for the code
  ([`771837f`](https://github.com/8-bit-hunters/pudly/commit/771837f115bf64a13ca1847b90812d754b03b91c))

- :heavy_plus_sign: Add development dependencies to create mkdocs page
  ([`94e2b97`](https://github.com/8-bit-hunters/pudly/commit/94e2b978bf75ad0c124029666235ff173cc6f23d))

- :wrench: Add project links to pyproject.toml
  ([`82eef3a`](https://github.com/8-bit-hunters/pudly/commit/82eef3a0a7cf44e03169f45d51b8e4f84682f67b))

- :memo: Update README
  ([`b3b5ea2`](https://github.com/8-bit-hunters/pudly/commit/b3b5ea20dd217315c9aec39de716ddc9457c62dc))

- :bulb: Document library elements with docstrings.
  ([`66765d8`](https://github.com/8-bit-hunters/pudly/commit/66765d8a8aa43f5a92edf8c1370d3c60108685f0))

- :loud_sound: Show the file name in download progress logs
  ([`cd86894`](https://github.com/8-bit-hunters/pudly/commit/cd868940f011aa34cc2add14772e5da491dde17b))

- :white_check_mark: Add test to check download function end-to-end
  ([`8a817f1`](https://github.com/8-bit-hunters/pudly/commit/8a817f1b09d68b1e2fe7901bd846e00e5b7cfeb6))

- :recycle: Use classes to represent downloaded file in different stages
  ([`bce81d8`](https://github.com/8-bit-hunters/pudly/commit/bce81d8cd8930fc98d9e4e91cf961a47da34f28b))

- :recycle: Refactor code for readability
  ([`b16f14e`](https://github.com/8-bit-hunters/pudly/commit/b16f14ebbd85f7fcf813f288ffb6b7fdf71b0860))

- :coffin: Remove pydantic model definitions
  ([`9ae6ca1`](https://github.com/8-bit-hunters/pudly/commit/9ae6ca1332f4a9d77afa2ef55491eb829eb33b58))

- :recycle: Use Path type for open the file
  ([`aba6458`](https://github.com/8-bit-hunters/pudly/commit/aba645831932d65b0feab03a14cf1dc11699655b))

- :heavy_plus_sign: Add requests as dependency
  ([`31e8d36`](https://github.com/8-bit-hunters/pudly/commit/31e8d3606f6c120345e1294270a1ab72955b8ce1))

- :wrench: Change project name and add author
  ([`fb326dd`](https://github.com/8-bit-hunters/pudly/commit/fb326dd0ab1937d0e2b477d36f32c99d2ec41f36))


## v0.0.0 (2024-11-22)

### Other

- Initial commit
  ([`1886c50`](https://github.com/8-bit-hunters/pudly/commit/1886c5027a026c71d5fef50ef28cd32d122fd16e))
