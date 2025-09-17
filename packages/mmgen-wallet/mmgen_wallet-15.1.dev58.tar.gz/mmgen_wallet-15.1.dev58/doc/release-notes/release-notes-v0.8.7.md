### MMGen version 0.8.7 Release Notes

#### Assorted fixes/improvements:

  - Importing addresses with `--rescan` working again
  - Tracking and spending non-MMGen addresses now fully functional
  - `mmgen-txcreate`: improvements in unspent outputs display
  - `mmgen-txsign`: use bitcoind wallet dump as keylist fixed

  - Testnet support:
    + Practice sending transactions without risking funds
  	(free testnet coins: https://tpfaucet.appspot.com/)
    + Test suite fully supported
    + To enable, set `MMGEN_TESTNET` environment variable
