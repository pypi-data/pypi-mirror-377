# DataChunker API 参考

## DataChunker 类

### 构造函数

```python
DataChunker(
    chunk_size=500,
    output_dir="output",
    prefix="chunk",
    timestamp=True,
    parallel=False,
    workers=4,
    logger=None
)
```

### 方法

#### process(data)

处理数据并将其分割保存为JSON文件。

**参数**:

- `data` (list): 字典列表数据

**返回**:

- list: 所有保存的文件路径列表

#### process_stream(stream_generator)

处理流式数据并将其分割保存为JSON文件。

**参数**:

- `stream_generator` (generator): 生成字典数据的生成器

**返回**:

- list: 所有保存的文件路径列表

#### split(data)

将数据分割成多个固定大小的块。

**参数**:

- `data` (list): 字典列表数据

**返回**:

- generator: 每次产生一个数据分块

#### set_config(**kwargs)

动态更新配置参数。

**参数**:

- `**kwargs`: 配置参数键值对

#### get_file_list()

获取已保存的文件列表。

**返回**:

- list: 输出目录中的所有JSON文件路径

#### clear_output()

清空输出目录中的所有JSON文件。

**返回**:

- int: 删除的文件数量

## 工具函数

### generate_sample_data(size=3000)

生成示例数据用于测试。

### json_stream_reader(file_path)

流式读取大型JSON文件。

### read_json_file(file_path)

读取JSON文件。

### write_json_file(data, file_path, indent=2)

写入JSON文件。

## 异常类

### DataChunkerError

基异常类。

### FileSaveError

文件保存错误。

### ChunkSizeError

分块大小错误。

### InvalidDataError

无效数据错误。