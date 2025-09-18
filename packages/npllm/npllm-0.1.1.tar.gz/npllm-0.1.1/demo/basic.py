import logging
logging.basicConfig(level=logging.WARNING, format='%(name)s - %(levelname)s - %(message)s')
logging.getLogger('npllm').setLevel(logging.DEBUG)

from typing import List, Dict, Tuple, Union, Literal, Any
from dataclasses import dataclass

from npllm.core.llm import LLM

async def f_int():
    llm = LLM()
    i: int = await llm.reason("What is the sum from 1 to 100?")
    print(i)

async def f_float():
    llm = LLM()
    f: float = await llm.reason("What is the value of pi?")
    print(f)

async def f_bool():
    llm = LLM()
    b: bool = await llm.reason("Is the sky blue?")
    print(b)

async def f_str():
    llm = LLM()
    s: str = await llm.reason("What is the capital of France?")
    print(s)

async def f_list():
    llm = LLM()
    lst: List[int] = await llm.reason("What are the first five prime numbers?")
    print(lst)

async def f_dict():
    llm = LLM()
    d: Dict[str, int] = await llm.reason("What are the ages of Alice and Bob if Alice is 30 and Bob is 25?")
    print(d)

async def f_tuple():
    llm = LLM()
    t: Tuple[int, str, float] = await llm.reason("Provide a tuple with an integer, a string, and a float.")
    print(t)

async def f_tuple_with_no_type_annotation():
    llm = LLM()
    i, s, f = await llm.reason("Provide a tuple with an integer, a string, and a float.")
    print(i, s, f)

async def f_union():
    llm = LLM()
    u: Union[int, str] = await llm.reason("Provide either an integer or a string, but you prefer to provide a string.")
    print(u)

async def f_union_1():
    llm = LLM()
    u: int | str = await llm.reason("Provide either an integer or a string, but you prefer to provide a string.")
    print(u)

async def f_literal():
    llm = LLM()
    l: Literal['red', 'green', 'blue'] = await llm.reason("Choose a color from red, green, or blue.")
    print(l)

@dataclass
class Address:
    street: str
    city: str
    zip_code: str

@dataclass
class Person:
    name: str
    age: int
    height: float
    address: Address

async def f_dataclass():
    llm = LLM()
    p: Person = await llm.reason("Create a Person object with name 'John Doe', age 30, height 5.9, and address '123 Main St, Anytown, 12345'.")
    print(p)

async def f_if():
    llm = LLM()
    if await llm.reason("Is 2 + 2 equal to 4?"):
        print("Yes, it is.")
    else:
        print("No, it isn't.")

async def f_while():
    llm = LLM()
    count = 0
    while await llm.reason("Is count less than 3?", count):
        print(f"Count is {count}")
        count += 1
    print("Finished counting.")

async def main():
    await f_int()
    await f_float()
    await f_bool()
    await f_str()
    await f_list()
    await f_dict()
    await f_tuple()
    await f_tuple_with_no_type_annotation()
    await f_union()
    await f_union_1()
    await f_literal()
    await f_dataclass()
    await f_if()
    await f_while()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())