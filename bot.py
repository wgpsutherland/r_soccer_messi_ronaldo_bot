from datetime import datetime
import praw

def build_comment_url_from_comment(comment):
    return 'https://www.reddit.com/comments/' + comment.link_id.replace('t3_', '') + '/_/' + comment.id


def days_hours_minutes_seconds(td):
    return td.days, td.seconds // 3600, (td.seconds // 60) % 60, td.seconds % 60


def format_time_string(time):

    days, hours, minutes, seconds = time

    s_days = str(days) + ' days, '
    s_hours = str(hours) + ' hours, '
    s_minutes = str(minutes) + ' minutes '
    s_seconds = str(seconds) + ' seconds'

    if days > 0:
        string = s_days + s_hours + s_minutes + 'and ' + s_seconds
    elif hours > 0:
        string = s_hours + s_minutes + 'and ' + s_seconds
    elif minutes > 0:
        string = s_minutes + 'and ' + s_seconds
    else:
        string = s_seconds

    return string


def build_reddit_comment(thread_subject, comment_subject, time, comment_object):
    comment = 'In this thread about ' + thread_subject + ', it took ' + format_time_string(time) + ' for someone to mention ' + comment_subject + ', in this comment [here](' + build_comment_url_from_comment(comment_object) + ').'
    return comment


def do_bot_stuff(comment, bot, comment_subject):

    print 'TITLE:', comment.link_title
    print 'COMMENT:', comment.body

    submission = comment.submission
    submission.comment_sort = 'old'
    submission.comments.replace_more(limit=None, threshold=0)
    comments = submission.comments.list()

    for x in comments:

        if comment_subject in x.body.lower():

            # add the submission id to the file so the bot does not post to it again
            with open("commented.txt", "a") as myfile:
                myfile.write(comment.link_id + '\n')

            time_difference = datetime.utcfromtimestamp(x.created_utc) - datetime.utcfromtimestamp(submission.created_utc)
            time_difference_parsed = days_hours_minutes_seconds(time_difference)

            if comment_subject == 'messi':
                built_comment = build_reddit_comment('Cristiano Ronaldo', 'Lionel Messi', time_difference_parsed, x)
            elif comment_subject == 'ronaldo':
                built_comment = build_reddit_comment('Lionel Messi', 'Cristiano Ronaldo', time_difference_parsed, x)

            bot.submission(submission.id).reply(built_comment)

            print 'BOT:', built_comment, '\n'
            
            break  # does not need to go through any more of the comments in the submission


r_messi = praw.Reddit('messiBot')
r_ronaldo = praw.Reddit('ronaldoBot')

subreddit = r_messi.subreddit('testingground4bots')

for comment in subreddit.stream.comments():

    title = comment.link_title.lower()
    body = comment.body.lower()

    if 'ronaldo' in title and 'messi' in title:
        continue

    if ('ronaldo' in title and 'messi' in body) or ('messi' in title and 'ronaldo' in body):
        examined_submissions = set(open("commented.txt").read().splitlines())
        if comment.link_id in examined_submissions:
            continue

    if 'ronaldo' in title and 'messi' in body:
        do_bot_stuff(comment, r_messi, 'messi')

    if 'messi' in title and 'ronaldo' in body:
        do_bot_stuff(comment, r_ronaldo, 'ronaldo')
