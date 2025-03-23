# config/settings.py
CONFIG = {
    'exchanges': {
        'cex': {
            'api_key': '8d117c7a6896a81170b0f7756b5afbe505ecf76b4139ad148cfaca80d512f8a4',
            'api_secret': '849e3cb1caf73922383a63603dba6d3a4618dd39e749aea9fffe5cabe5c4b741'
        },
        'kraken': {
            'api_key': 'EObacx/wiSkywapsFDP2CgBTIjSLV7bAZnRJHKsSNLQ11t8ssEm+6agA',
            'api_secret': 'a178EC9lv1J3l+72TVsUSH1zycczLeNjX4rhaiALqga88XXByy5thhb4RRKJdTgAApYs2my7lageslBqrS/l1w=='
        }
    },
    'symbol_pairs': ['BTC/USD', 'ETH/USD', 'ETH/BTC'],  # Pairs supported by both CEX.io and Kraken
    'min_profit': 0.3,  # Minimum profit percentage
    'trade_amount': 0.01,  # Base currency amount
    'cooldown': 30,  # Seconds between trades
    'slippage_tolerance': 0.005,  # 0.5% slippage tolerance
    'poll_interval': 2,  # Seconds between market scans
    'max_trade_amount': 0.1  # Maximum trade amount
}