from fetch_pjm_realtime_lmp_market_prices import get_pjm_rt_lmp
from fetch_nyiso_realtime_lmp_market_prices import get_nyiso_rt_lmp
from fetch_caiso_realtime_lmp_market_prices import get_caiso_rt_lmp
from fetch_miso_realtime_lmp_market_prices import get_miso_rt_lmp
from fetch_spp_realtime_lmp_market_prices import get_spp_rt_lmp
from fetch_ercot_realtime_lmp_market_prices import get_ercot_rt_lmp

def fetch_realtime_electricity_price(rto_iso, years):
    if rto_iso == 'pjm':
        df = get_pjm_rt_lmp(years)
    elif rto_iso == 'nyiso':
        df = get_nyiso_rt_lmp(years)
    elif rto_iso == 'caiso':
        df = get_caiso_rt_lmp(years)
    elif rto_iso == 'miso':
        df = get_miso_rt_lmp(years)
    elif rto_iso == 'spp':
        df = get_spp_rt_lmp(years)
    elif rto_iso == 'ercot':
        df = get_ercot_rt_lmp(years)
    else:
        raise ValueError(f"Unsupported RTO/ISO: {rto_iso}")
    
    return df

# Example usage
if __name__ == "__main__":
    rto_iso = 'ercot'
    years = [2021, 2022]
    prices = fetch_realtime_electricity_price(rto_iso, years)
    print(prices.head())
    print(prices.tail())