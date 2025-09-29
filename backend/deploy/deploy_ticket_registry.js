async function main() {
  const TicketRegistry = await ethers.getContractFactory("TicketRegistry");
  const registry = await TicketRegistry.deploy();
  await registry.deployed();
  console.log("TicketRegistry deployed to:", registry.address);
}
main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
