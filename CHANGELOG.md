# v0.1.4 (2018-02-09)

 - Updated versions for dependencies

# v0.1.3 (2018-01-26)

 - Quoted controller_mirror_ports to allow for special characters
 - Fixed mirroring for FAUCET
 - Better error checking for the helper script
 - Clarify some documentation
 - Set defaults for log and config files for FAUCET

# v0.1.2 (2018-01-12)

 - Fixed bug where mirroring was backwards for FAUCET (thanks @alshaboti)
 - Improved the helper run script to be easier
 - Removed Elasticsearch and RMQ-to-ES containers from Vent build and runtime for Poseidon

# v0.1.1 (2017-12-15)

 - New feature if poseidon and faucet on the same host, doesn't require ssh/scp
 - Various bug fixes

# v0.1.0 (2017-12-04)

 - Initial release
 - Basic functionality with Big Cloud Fabric and FAUCET controllers
 - Can be run as a standalone Docker container or orchestrated through Vent.
