# Architecture

The browser loads native ES modules without a Node build pipeline. All NASA requests go through the same-origin Python gateway. Data adapters normalize provider responses independently of UI and statistics. This keeps credentials, future Earthdata processing, and scientific computation on the server.

## Data contract

Observation responses contain source, exact source request URL, variable, native unit, latitude/longitude, temporal/spatial resolution notes, latest valid date within the requested selection, provider publication time (null when unknown), retrieval timestamp, original provider header, fill value, WGS84 reference, and daily `{date, value}` rows. Missing values are null. Successful data may contain an analysis error when the series is unsuitable for inference.

## Analysis

Annual and monthly means use valid daily observations. Precipitation uses totals. Periods below 90% calendar coverage are excluded, including incomplete boundary periods. Partial precipitation coverage can underestimate totals and is disclosed. Optional monthly deseasonalization subtracts each calendar month's mean over the selected period. Dates become fractional years based on actual elapsed days.

SciPy ordinary least squares estimates slope and a two-sided Student-t 95% slope interval. Mann–Kendall includes tie correction and continuity correction. Both tests assume independence; residual lag-1 correlation is reported but significance is **not** autocorrelation-adjusted. These are exploratory results. Constant series return slope zero and p=1. Wind direction requires circular methods and has no ordinary trend result. Analyses need at least three complete periods and cap quadratic Mann–Kendall work at 1500 periods.

## Operational boundaries

NASA requests have a 45-second timeout. A bounded 128-entry memory cache retains successful requests for 24 hours; retrieval timestamps remain original on cache hits. Dates and coordinates are validated server-side; date spans are limited to 45 years. Loopback hosting is the access boundary, not an authentication mechanism.

Before any hosted use: implement authentication, per-user rate limits and request concurrency limits, shared cache, production dependency locking, observability, and worker queues for Earthdata tasks. Credentials belong in server environment variables. Do not publish without explicit approval.

Future adapters should use the same normalized contract and expose supported capabilities explicitly. AppEEARS requires persistent task IDs and asynchronous job polling; regional calculations require actual grid-cell area weighting and quality masks. Never approximate regions using arbitrary city samples.

## Map interface

MapLibre GL JS is vendored in frontend/vendor and renders a 2D Web Mercator map using NASA GIBS WMS rasters. Each tab selects a distinct supported layer. NASA imagery dates are independent of POWER query dates. AOD imagery is not presented as local air temperature or an extractable AOD measurement. Clicking the map centers the marker and populates the numerical coordinates; only Atmosphere initiates a POWER request. Query changes abort obsolete requests and clear prior readings to avoid displaying values for the wrong point, variable or period. The page header, five navigation tabs, point panel, chart container and map controls are static HTML, with JavaScript updating their state.
