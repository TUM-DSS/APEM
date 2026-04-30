# Datasets

APEM includes built-in datasets for the unit-based and order-book-based workflows. Select them through [`config.json`](https://github.com/teodora-dobos/APEM/blob/main/config.json).

For configuration syntax, see [](configuration). For adding your own data, see [](custom_datasets).

## Unit-Based Datasets

Use these values under `unit_based_model.dataset`.

| Dataset key | Description | Notes |
|---|---|---|
| `IEEE_RTS` | [IEEE Reliability Test System](https://labs.ece.uw.edu/pstca/rts/pg_tcarts.htm)-style unit-based scenario, based on the RTS-96 test system described by Grigg et al. (1999). | Generation-cost and demand-valuation bid/offer curves follow the case studies of Garcia-Bertrand et al. (2006) and Zoltowska (2016). Also available as a converted order-book dataset. Supports the nodal unit-based workflows. |
| `PJM` | Single-node PJM day-ahead-market dataset included in the repository. | Repository data is for 28 February 2023. Uses many seller offer blocks and generated buyer valuations. Source data is based on [PJM Data Miner 2](https://dataminer2.pjm.com/list). Supports the nodal unit-based workflows. |
| `PyPSAEurSmall` | Small [PyPSA-Eur](https://pypsa-eur.readthedocs.io/en/latest/)-derived unit-based scenario for Germany. | Data is for 1 March 2013. Supports the nodal and zonal unit-based workflows. |
| `PyPSAEurLarge` | Large [PyPSA-Eur](https://pypsa-eur.readthedocs.io/en/latest/)-derived unit-based scenario for Germany. | Data is for 1 March 2013. Supports the nodal and zonal unit-based workflows. |
| `ARPA` | [ARPA-E Grid Optimization Competition](https://data.openei.org/submissions/6197)-derived unit-based network scenario. | Single-period scenario. Supports the nodal unit-based workflows. Used by APEM PF Relaxations and also available as a converted order-book dataset. |

```{note}
The zonal unit-based workflows (`Zonal_NTC_aggregated`, `Zonal_NTC_multiedge`, and `Zonal_FBMC`) are currently supported for `PyPSAEurSmall` and `PyPSAEurLarge`.
```

### Unit-Based Dataset Sizes

The counts below are computed from the parsed `Scenario` objects. Branches are transmission-network graph edges. Seller and buyer counts are unique seller and buyer IDs.

| Dataset key | Nodes | Branches | Sellers | Buyers |
|---|---:|---:|---:|---:|
| `IEEE_RTS` | 25 | 34 | 32 | 17 |
| `PJM` | 1 | 0 | 457 | 3 |
| `PyPSAEurSmall` | 40 | 67 | 246 | 40 |
| `PyPSAEurLarge` | 328 | 431 | 1078 | 252 |
| `ARPA` | 617 | 841 | 94 | 404 |

## Order-Book-Based Datasets

Use these values under `order_book_based_model.dataset`.

| Dataset key | Description | Notes |
|---|---|---|
| `GENERATED_SMALL` | Generated Euphemia-style order-book instance. | Useful for small order-book experiments. |
| `GENERATED_LARGE` | Larger generated Euphemia-style order-book instance. | Useful for larger generated order-book experiments. |
| `OMIE` | OMIE day-ahead-market file-format-based dataset. | See the dataset README under `apem/order_book_based_model/euphemia/data/datasets/omie/`. |
| `GME` | GME order-book dataset. | Loaded from the bundled Euphemia-style CSV folder. |
| `TEST_3NODE` | Small 3-zone test instance. | Includes ATC and FBMC inputs; useful for validating network constraints. |
| `TEST_3NODE_LOWCAP` | Low-capacity variant of `TEST_3NODE`. | Same structure as `TEST_3NODE`, with lower capacities. |
| `IEEE_RTS` | Order-book version of `IEEE_RTS`. | Obtained through the unit-based-to-order-book conversion workflow. |
| `ARPA` | Order-book version of `ARPA`. | Obtained through the unit-based-to-order-book conversion workflow. |

Order-book datasets are stored as Euphemia-style CSV folders under:

```text
apem/order_book_based_model/euphemia/data/datasets/
```

## Dataset Conversion

APEM can convert selected unit-based scenarios into order-book CSV inputs. This is used for the order-book versions of `IEEE_RTS` and `ARPA`.

The conversion utilities live under:

```text
apem/order_book_based_model/euphemia/data/conversion/
```

For implementation details, see [](apem/order_book_based_model/data_parsing).

## References

- Grigg C, Wong P, Albrecht P, Allan R, Bhavaraju M, Billinton R, Chen Q, Fong C, Haddad S, Kuruganty S, Li W, Mukerji R, Patton D, Rau N, Reppen D, Schneider A, Shahidehpour M, Singh C (1999). [The IEEE reliability test system 1996](https://doi.org/10.1109/59.780914). *IEEE Transactions on Power Systems*, 14(3):1010-1020.
- Garcia-Bertrand R, Conejo AJ, Gabriel S (2006). [Electricity market near-equilibrium under locational marginal pricing and minimum profit conditions](http://dx.doi.org/10.1016/j.ejor.2005.03.037). *European Journal of Operational Research*, 174(1):457-479.
- Zoltowska I (2016). [Demand shifting bids in energy auction with non-convexities and transmission constraints](http://dx.doi.org/10.1016/j.eneco.2015.05.016). *Energy Economics*, 53:17-27.
