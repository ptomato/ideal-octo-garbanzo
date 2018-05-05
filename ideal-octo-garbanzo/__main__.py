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


@router.register('pull_request', action='closed')
async def pull_request_closed_event(event, gh, *args, **kwargs):
    """Whenever a pull request is merged, thank the author."""
    merged = event.data['pull_request']['merged']
    if not merged:
        return

    url = event.data['pull_request']['comments_url']
    author = event.data['pull_request']['user']['login']
    repo = event.data['pull_request']['base']['repo']['full_name']
    message = f""":pizza: Thanks for all the hard work, @{author}! We love it
when people help make {repo} better. :sushi:

—Sincerely, ideal-:octocat:-garbanzo the Bot"""
    await gh.post(url, data={'body': message})


@router.register('issue_comment', action='created')
async def issue_comment_created_event(event, gh, *args, **kwargs):
    """Whenever ptomato comments, give him a thumbs up."""
    user = event.data['comment']['user']['login']
    if user != 'ptomato':
        return

    url = event.data['comment']['url'] + '/reactions'
    await gh.post(url, data={'content': 'heart'},
                  accept='application/vnd.github.squirrel-girl-preview+json')


@router.register('pull_request', action='opened')
async def pull_request_opened_event(event, gh, *args, **kwargs):
    """Whenever a pull request is opened, give it the "Review Ready" label."""
    url = event.data['pull_request']['url']
    pull_request = await gh.getitem(url)
    labels = [label['name'] for label in pull_request['labels']]
    labels += ['Review Ready']
    await gh.patch(url, data={'labels': labels})


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
