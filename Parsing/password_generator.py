#Password Generator
import random
letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
symbols = ['!', '#', '$', '%', '&', '(', ')', '*', '+']

print("Welcome to the PyPassword Generator!")
nr_letters= int(input("How many letters would you like in your password?\n")) 
nr_symbols = int(input(f"How many symbols would you like?\n"))
nr_numbers = int(input(f"How many numbers would you like?\n"))
password = ''
source = ''
source = nr_letters*'L' + nr_symbols*'S' + nr_numbers*'N'
password_len = len(source)

for i in range(password_len):
  action = random.choice(source)
  if action == 'L': # choose letter
    index = random.randint(0,len(letters)-1)
    password += letters[index]
    source.replace('L', '')
  elif action == 'S': # choose symbols
    index = random.randint(0,len(symbols)-1)
    password += symbols[index]
    source.replace('S', '')
  elif action == 'N': # choose number
    index = random.randint(0,len(numbers)-1)
    password += numbers[index]
    source.replace('N', '')

print(password)
