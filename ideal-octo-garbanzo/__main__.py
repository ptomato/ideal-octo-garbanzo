import aiohttp
import os
from aiohttp import web
from gidgethub import routing, sansio
from gidgethub import aiohttp as gh_aiohttp

router = routing.Router()


@router.register('issues', action='opened')
async def issue_opened_event(event, gh, *args, **kwargs):
    """Whenever an issue is opened, greet the author and say thanks."""
    url = event.data['issue']['comments_url']
    author = event.data['issue']['user']['login']
    message = f"""Thanks for the report @{author}! :tada: A maintainer will be
along soon to take a look.

:doughnut: We appreciate your taking the time to file a bug report. :doughnut:

—Sincerely, ideal-:octocat:-garbanzo the Bot"""
    await gh.post(url, data={'body': message})


async def main(request):
    body = await request.read()
    secret = os.environ.get('GH_SECRET')
    token = os.environ.get('GH_AUTH')

    event = sansio.Event.from_http(request.headers, body, secret=secret)

    async with aiohttp.ClientSession() as session:
        gh = gh_aiohttp.GitHubAPI(session, 'ptomato', oauth_token=token)
        await router.dispatch(event, gh)

    return web.Response(status=200)


if __name__ == '__main__':
    app = web.Application()
    app.router.add_post('/', main)
    port = os.environ.get('PORT')
    if port is not None:
        port = int(port)

    web.run_app(app, port=port)
