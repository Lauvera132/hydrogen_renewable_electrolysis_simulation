from fetch_pjm_realtime_lmp_market_prices import get_pjm_rt_lmp
from fetch_nyiso_realtime_lmp_market_prices import get_nyiso_rt_lmp
from fetch_caiso_realtime_lmp_market_prices import get_caiso_rt_lmp
from fetch_miso_realtime_lmp_market_prices import get_miso_rt_lmp
from fetch_spp_realtime_lmp_market_prices import get_spp_rt_lmp
from fetch_ercot_realtime_lmp_market_prices import get_ercot_rt_lmp

def get_rto_iso_rt_lmp(rto_iso, years):
    if rto_iso == 'PJM':
        df = get_pjm_rt_lmp(years)
    elif rto_iso == 'NYISO':
        df = get_nyiso_rt_lmp(years)
    elif rto_iso == 'CAISO':
        df = get_caiso_rt_lmp(years)
    elif rto_iso == 'MISO':
        df = get_miso_rt_lmp(years)
    elif rto_iso == 'SPP':
        df = get_spp_rt_lmp(years)
    elif rto_iso == 'ERCOT':
        df = get_ercot_rt_lmp(years)
    else:
        raise ValueError(f"Unsupported RTO/ISO: {rto_iso}")
    
    return df

# Example usage
if __name__ == "__main__":
    rto_iso = 'ERCOT'
    years = [2021, 2022]
    prices = get_rto_iso_rt_lmp(rto_iso, years)
    print(prices.head())
    print(prices.tail())