// GeneTech 14站跨站搜索
const KB_SITES = {
  genetech: "https://genetech-tools.pages.dev/api/entities.json",
  tcm: "https://tcm-tools.pages.dev/api/entities.json",
  brain: "https://brainscience.pages.dev/api/entities.json",
  quantum: "https://quantumcomputing.pages.dev/api/entities.json",
  nuclear: "https://nuclearenergy.pages.dev/api/entities.json",
  exo: "https://exoscience.pages.dev/api/entities.json",
  alien: "https://alienminerals.pages.dev/api/entities.json",
  deepsea: "https://deepseatech.pages.dev/api/entities.json",
  newenergy: "https://newenergy-nya.pages.dev/api/entities.json",
  lifescience: "https://lifescience-epe.pages.dev/api/entities.json",
  biocomputing: "https://biocomputedb.pages.dev/api/entities.json",
  bionicai: "https://bionicai.pages.dev/api/entities.json",
  agent: "https://agentecosystem.pages.dev/api/entities.json",
  robot: "https://robotparts.pages.dev/api/entities.json"
};

async function crossSiteSearch(keyword) {
  const results = {};
  const promises = Object.entries(KB_SITES).map(async ([site, url]) => {
    try {
      const resp = await fetch(url);
      const data = await resp.json();
      const entities = Array.isArray(data) ? data : (data.entities || data.data || []);
      const matches = entities.filter(e => 
        JSON.stringify(e).toLowerCase().includes(keyword.toLowerCase())
      ).slice(0, 5);
      if (matches.length > 0) results[site] = matches;
    } catch (e) {}
  });
  await Promise.all(promises);
  return results;
}
