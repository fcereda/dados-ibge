# dados-ibge
Python scripts that uses IBGE socioeconomic data on Brazilian cities to build a CSV file to be used by Atlas Eleitoral.  

## How it works
Just run: 
```
python3 ibge
```

Since the script uses IBGE's API to get IDH data for every municipality in Brazil, it takes a while (~1 hour) to complete.

If all goes well, the script will produce a file named `municipios.csv` containing several socieconomic indexes for each Brazilian municipality, indexed by IBGE's code.  
