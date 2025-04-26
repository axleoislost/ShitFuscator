import random
import base64

def generate_random_name():
    chars = 'abcdefghijklmnopqrstuvwxyz'
    return ''.join(random.choice(chars) for _ in range(5))

def custom_encrypt(text, key):
    result = []
    for i, c in enumerate(text):
        encrypted_byte = (ord(c) + (i + 1) + key) % 256
        result.append(encrypted_byte)
    return result

def fake_array(length=50):
    return ",".join(str(random.randint(0, 255)) for _ in range(length))

def generate_fake_code():
    fake_code = []
    fake_code.append(f"local {generate_random_name()} = {random.randint(1, 100)}")
    fake_code.append(f"local {generate_random_name()} = function() end")
    fake_code.append(f"local {generate_random_name()} = function(a, b) return a + b end")
    fake_code.append(f"local {generate_random_name()} = {random.randint(100, 1000)}")
    fake_code.append(f"local {generate_random_name()} = {{ {fake_array(20)} }}")
    fake_code.append(f"local {generate_random_name()} = {{ {fake_array(15)} }}")
    fake_code.append(f"local function {generate_random_name()}() return end")
    return "\n".join(fake_code)

def generate_fake_code_stage2():
    fake_code = []
    fake_code.append(f"local {generate_random_name()} = function(a) return a * 2 end")
    fake_code.append(f"local {generate_random_name()} = function(a, b) return a - b end")
    fake_code.append(f"local {generate_random_name()} = {random.randint(2000, 3000)}")
    fake_code.append(f"local {generate_random_name()} = {{ {fake_array(40)} }}")
    fake_code.append(f"local {generate_random_name()} = {{ {fake_array(25)} }}")
    fake_code.append(f"local function {generate_random_name()}() return 0 end")
    return "\n".join(fake_code)

def obfuscate(source):
    key = random.randint(20, 200)
    encrypted_real = custom_encrypt(source, key)
    real_array = ",".join(str(num) for num in encrypted_real)
    num_fake_arrays = random.randint(2, 5)
    arrays = []
    for _ in range(num_fake_arrays):
        arrays.append(fake_array(random.randint(30, 80)))
    arrays.append(real_array)
    random.shuffle(arrays)
    env_var = generate_random_name()
    ascii_var = generate_random_name()
    load_func_var = generate_random_name()
    decrypt_func_var = generate_random_name()
    key_var = generate_random_name()
    array_vars = [generate_random_name() for _ in arrays]
    lua_stub = f'''
{generate_fake_code()}

local {env_var} = getfenv and getfenv(1) or _ENV
local {ascii_var} = {{108,111,97,100,115,116,114,105,110,103}}
local b = ""
for _, v in ipairs({ascii_var}) do
    b = b .. string.char(v)
end
local {load_func_var} = {env_var}[b]
'''
    for name, arr in zip(array_vars, arrays):
        lua_stub += f'local {name} = {{{arr}}}\n'
    for _ in range(random.randint(2, 5)):
        dummy_func_name = generate_random_name()
        dummy_array = random.choice(array_vars)
        lua_stub += f'''
local function {dummy_func_name}(tbl, key)
    local str = ""
    for i = #tbl, 1, -1 do
        local c = (tbl[i] + i + key) % 256
        str = str .. string.char(c)
    end
    return str
end
'''
    lua_stub += f'''
local function {decrypt_func_var}(tbl, key)
    local str = ""
    for i = 1, #tbl do
        local c = (tbl[i] - i - key) % 256
        str = str .. string.char(c)
    end
    return str
end
'''
    real_array_var = array_vars[arrays.index(real_array)]
    lua_stub += f'''
local {key_var} = {key}
{load_func_var}({decrypt_func_var}({real_array_var}, {key_var}))()
'''
    lua_stub += f"\n{generate_fake_code_stage2()}"
    return lua_stub

def final_wrap(lua_code):
    stage1_obfuscated = obfuscate(lua_code)
    stage2_obfuscated = obfuscate(stage1_obfuscated)
    encoded = base64.b64encode(stage2_obfuscated.encode()).decode()
    reversed_encoded = encoded[::-1]
    final_lua = f'loadstring(base64_decode(string.reverse("{reversed_encoded}")))()'
    return final_lua

def obfuscate_lua_file(input_file, output_file):
    with open(input_file, 'r') as f:
        lua_code = f.read()
    final_output = final_wrap(lua_code)
    with open(output_file, 'w') as f:
        f.write(final_output)

input_lua = 'input.lua'
output_lua = 'output.lua'
obfuscate_lua_file(input_lua, output_lua)
