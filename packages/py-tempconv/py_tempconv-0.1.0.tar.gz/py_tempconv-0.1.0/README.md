TempConversion
Conversion between different temperature units To convert, just call the appropriate function. Each conversion has it's own function. All temperature scales have been denoted by an abbreviation. Celsius - C, Fahrenheit - F, Kelvin - K, Rankine - R, Newton - N, Delisle - D, Romer - Ro, Reaumur - Rea

So accordingly, the function to convert from Celsius to Fahrenheit is : C_to_F(), the function function to convert from Rankine to Romer is: R_to_Ro() and so on.

Syntax:

import py_tempconv

# Example of converting 100 degrees Celsius to Fahrenheit
temp_in_f = py_tempconv.C_to_F(100)
print(temp_in_f)