import json
import re
import grequests
import requests
from flask import Flask

from flask import jsonify
from bs4 import BeautifulSoup

from flask_cors import CORS
from flask_restful import Api, Resource

app = Flask(__name__)
CORS(app)
api = Api(app)


@app.route('/codechef/<username>', methods=['GET'])
def getUser(username):
    
    url = 'https://www.codechef.com/users/{}'.format(username)
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')

    try:
            rating = soup.find('div', class_='rating-number').text
            

            stars = soup.find('span', class_='rating')
            f = open("index.html", "a")
            f.write(str(soup))
            f.close()
            if stars:
                stars = stars.text

            highest_rating_container = soup.find('div', class_='rating-header')
            highest_rating = highest_rating_container.find_next('small').text.split()[-1].rstrip(')')

            rating_ranks_container = soup.find('div', class_='rating-ranks')
            rating_ranks = rating_ranks_container.find_all('a')

            global_rank = rating_ranks[0].strong.text
            country_rank = rating_ranks[1].strong.text

            if global_rank != 'NA':
                global_rank = int(global_rank)
                country_rank = int(country_rank)

            def contests_details_get():
                rating_table = soup.find('table', class_='rating-table')

                rating_table_rows = rating_table.find_all('td')

                '''Can add ranking url to contests'''

                try:
                    long_challenge = {'name': 'Long Challenge', 'rating': int(rating_table_rows[1].text),
                                    'global_rank': int(rating_table_rows[2].a.hx.text),
                                    'country_rank': int(rating_table_rows[3].a.hx.text)}

                except ValueError:
                    long_challenge = {'name': 'Long Challenge', 'rating': int(rating_table_rows[1].text),
                                    'global_rank': rating_table_rows[2].a.hx.text,
                                    'country_rank': rating_table_rows[3].a.hx.text}

                try:
                    cook_off = {'name': 'Cook-off',
                                'rating': int(rating_table_rows[5].text),
                                'global_rank': int(rating_table_rows[6].a.hx.text),
                                'country_rank': int(rating_table_rows[7].a.hx.text)}
                except ValueError:
                    cook_off = {'name': 'Cook-off',
                                'rating': int(rating_table_rows[5].text),
                                'global_rank': rating_table_rows[6].a.hx.text,
                                'country_rank': rating_table_rows[7].a.hx.text}

                try:
                    lunch_time = {'name': 'Lunch Time', 'rating': int(rating_table_rows[9].text),
                                'global_rank': int(rating_table_rows[10].a.hx.text),
                                'country_rank': int(rating_table_rows[11].a.hx.text)}

                except ValueError:
                    lunch_time = {'name': 'Lunch Time', 'rating': int(rating_table_rows[9].text),
                                'global_rank': rating_table_rows[10].a.hx.text,
                                'country_rank': rating_table_rows[11].a.hx.text}

                return [long_challenge, cook_off, lunch_time]
           

             
                # graph = content.find("div", {"id": "submissions-graph"})
                
            def contest_rating_details_get():
                
                start_ind = page.text.find('[', page.text.find('all_rating'))
                end_ind = page.text.find(']', start_ind) + 1

                next_opening_brack = page.text.find('[', start_ind + 1)
                while next_opening_brack < end_ind:
                    end_ind = page.text.find(']', end_ind + 1) + 1
                    next_opening_brack = page.text.find('[', next_opening_brack + 1)

                all_rating = json.loads(page.text[start_ind: end_ind])
                for rating_contest in all_rating:
                    rating_contest.pop('color')

                return all_rating

            def problems_solved_get():
                problem_solved_section = soup.find('section', class_='rating-data-section problems-solved')

                no_solved = problem_solved_section.find_all('h5')

                categories = problem_solved_section.find_all('article')

                fully_solved = {'count': int(re.findall(r'\d+', no_solved[0].text)[0])}

                if fully_solved['count'] != 0:
                    for category in categories[0].find_all('p'):
                        category_name = category.find('strong').text[:-1]
                        fully_solved[category_name] = []

                        for prob in category.find_all('a'):
                            fully_solved[category_name].append({'name': prob.text,
                                                                'link': 'https://www.codechef.com' + prob['href']})

                partially_solved = {'count': int(re.findall(r'\d+', no_solved[1].text)[0])}
                if partially_solved['count'] != 0:
                    for category in categories[1].find_all('p'):
                        category_name = category.find('strong').text[:-1]
                        partially_solved[category_name] = []

                        for prob in category.find_all('a'):
                            partially_solved[category_name].append({'name': prob.text,
                                                                    'link': 'https://www.codechef.com' + prob['href']})

                return fully_solved, partially_solved

            def user_details_get():
                user_details_attribute_exclusion_list = {'username', 'link', 'teams list', 'discuss profile'}

                header_containers = soup.find_all('header')
                name = header_containers[1].find('h1', class_="h2-style").text

                user_details_section = soup.find('section', class_='user-details')
                user_details_list = user_details_section.find_all('li')

                user_details_response = {'name': name, 'username': user_details_list[0].text.split('★')[-1].rstrip('\n')}
                for user_details in user_details_list:
                    attribute, value = user_details.text.split(':')[:2]
                    attribute = attribute.strip().lower()
                    value = value.strip()

                    if attribute not in user_details_attribute_exclusion_list:
                        user_details_response[attribute] = value
                return user_details_response
            full, partial = problems_solved_get()
            
            details = {'success': True, 'user_details': user_details_get(),'rating': int(rating), 'stars': stars, 'highest_rating': int(highest_rating),
                   'global_rank': global_rank, 'country_rank': country_rank,
                    'contests': contests_details_get(),
                   'contest_ratings': contest_rating_details_get(), 'fully_solved': full, 'partially_solved': partial}

            return jsonify(details), 200

             
    except AttributeError:
            data = {'success': False, 'message' : 'Please provide a valid username'}
            return jsonify(data), 400

    
    
    
@app.route('/codeforces/<username>', methods=['GET'])
def codeforces(username):
 
        urls = {
            "user_info": {"url": f'https://codeforces.com/api/user.info?handles={username}'},
            "user_contests": {"url": f'https://codeforces.com/contests/with/{username}'}
        }

        reqs = [grequests.get(item["url"]) for item in urls.values() if item.get("url")]

        responses = grequests.map(reqs)

        details_api = {}
        contests = []
        for page in responses:
            if page.status_code != 200:
                data = {'success': False, 'message' : 'Please provide a valid username'}
                return jsonify(data), 400
            if page.request.url == urls["user_info"]["url"]:
                details_api = page.json()
            elif page.request.url == urls["user_contests"]["url"]:
                soup = BeautifulSoup(page.text, 'html.parser')
                table = soup.find('table', attrs={'class': 'user-contests-table'})
                table_body = table.find('tbody')

                rows = table_body.find_all('tr')
                for row in rows:
                    cols = row.find_all('td')
                    cols = [ele.text.strip() for ele in cols]
                    contests.append({
                        "Contest": cols[1],
                        "Rank": cols[3],
                        "Solved": cols[4],
                        "Rating Change": cols[5],
                        "New Rating": cols[6]
                    })

        if details_api.get('status') != 'OK':
            data = {'success': False, 'message' : 'Please provide a valid username'}
            return jsonify(data), 400

        details_api = details_api['result'][0]

        try:
            rating = details_api['rating']
            max_rating = details_api['maxRating']
            rank = details_api['rank']
            max_rank = details_api['maxRank']

        except KeyError:
            rating = 'Unrated'
            max_rating = 'Unrated'
            rank = 'Unrated'
            max_rank = 'Unrated'

        return {
            'success' : True,
            'username': username,
            'platform': 'Codeforces',
            'rating': rating,
            'max rating': max_rating,
            'rank': rank,
            'max rank': max_rank,
            'contests': contests
        }
       
if __name__ == "__main__" :
    app.run()