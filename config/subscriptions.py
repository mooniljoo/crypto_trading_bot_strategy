# Not Auth Required
'''
"announcement",        // Site announcements
"chat",                // Trollbox chat
"connected",           // Statistics of connected users/bots
"funding",             // Updates of swap funding rates. Sent every funding interval (usually 8hrs)
"instrument",          // Instrument updates including turnover and bid/ask
"insurance",           // Daily Insurance Fund updates
"liquidation",         // Liquidation orders as they're entered into the book
"orderBookL2_25",      // Top 25 levels of level 2 order book
"orderBookL2",         // Full level 2 order book
"orderBook10",         // Top 10 levels using traditional full book push
"publicNotifications", // System-wide notifications (used for short-lived messages)
"quote",               // Top level of the book
"quoteBin1m",          // 1-minute quote bins
"quoteBin5m",          // 5-minute quote bins
"quoteBin1h",          // 1-hour quote bins
"quoteBin1d",          // 1-day quote bins
"settlement",          // Settlements
"trade",               // Live trades
"tradeBin1m",          // 1-minute trade bins
"tradeBin5m",          // 5-minute trade bins
"tradeBin1h",          // 1-hour trade bins
'''
# Auth Required
'''
"affiliate",   // Affiliate status, such as total referred users & payout %
"execution",   // Individual executions; can be multiple per order
"order",       // Live updates on your orders
"margin",      // Updates on your current account balance and margin requirements
"position",    // Updates on your positions
"privateNotifications", // Individual notifications - currently not used
"transact"     // Deposit/Withdrawal updates
"wallet"       // Bitcoin address balance data, including total deposits & withdrawals
'''
AUTH_SUBS = [
    "wallet",
    "position",
    "margin",
    "execution",
    "affiliate",
    "order"
]
NO_AUTH_SUBS = [
    "instrument",
    "quote",
    "trade",
    "liquidation",
    "orderBookL2"
]
# Most subscriptions take a symbol, but some do not.
NO_SYMBOL_SUBS = [
    "account",
    "affiliate",
    "announcement",
    "connected",
    "chat",
    "insurance",
    "margin",
    "publicNotifications",
    "privateNotifications",
    "transact",
    "wallet"
]
# By default, we subscribe to these tables. They can be overridden
# on websocket init via the "subscriptions" parameter.
DEFAULT_SUBS = [
    "execution",
    "instrument",
    "margin",
    "order",
    # You can sub to orderBookL2 for all levels, or orderBook10 for top 10 levels.
    # This will save bandwidth & processing time in many cases. OrderBook10 is a pulsed
    # table that sends all rows. For more on orderBook subscriptions, see
    # https://www.bitmex.com/app/wsAPI#Subscriptions
    "orderBookL2",
    "position",
    "quote",
    "trade",
    "wallet"
]
