# [AWESOMEPYUTIL](https://pypi.org/project/awesomepyutil/0.0.1/)

Simple python package.

# How To Use The Package

1. Install The Package
    ```shell
    pip install awesomepyutil==0.0.1
    ```
2. Use `Arithmetic Operations`
    ```shell
    from awesomepyutil.arithmetic_ops.arithmetic_operations import func_divide

    out = func_divide(5,2)
    print(f"out: {out}")

    # Out: 2.5
    ```

3. Use `NSE`
    ```shell
    from awesomepyutil.stock_market.nse import NSE
    
    # create NSE Object
    nse = NSE()
    
    # Get daily index gainers
    out = nse.get_index_gainers()
    print(out)
    
    # Get daily index loosers
    out = nse.get_index_loosers()
    print(out)
    
    out = nse.get_marketstate_daily()
    print(f"{out}")
    ```