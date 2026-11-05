// Каждые 30 минут запускает GitHub Actions workflow публикации постов в Threads.
// Секрет GH_TOKEN: fine-grained токен GitHub с правом Actions: Read and write на этот репозиторий.
const REPO = "oxionezhkov-hub/ai-zarabotok-sales";
const WORKFLOW = "threads-publish.yml";
const BRANCH = "claude/ecstatic-sagan-de82of";

async function dispatch(env) {
  const res = await fetch(
    `https://api.github.com/repos/${REPO}/actions/workflows/${WORKFLOW}/dispatches`,
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${env.GH_TOKEN}`,
        Accept: "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "threads-cron-worker",
      },
      body: JSON.stringify({ ref: BRANCH }),
    },
  );
  if (res.status !== 204) {
    throw new Error(`GitHub ответил ${res.status}: ${await res.text()}`);
  }
}

export default {
  async scheduled(event, env, ctx) {
    ctx.waitUntil(dispatch(env));
  },
  // По ссылке воркера ничего не запускается, только видно, что он жив.
  async fetch() {
    return new Response("threads-cron: работает по расписанию", {
      headers: { "content-type": "text/plain; charset=utf-8" },
    });
  },
};
