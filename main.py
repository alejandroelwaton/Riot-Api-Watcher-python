from riotwatcher import ApiError
import objects


def main():
    json_data = objects.get_JSON_api_key('data.json')
    api_key = json_data
    name = input('Enter summoner name: ')
    print(api_key)
    lol = objects.Player(api_key, 'la1', name)
    lol.show_info_ofline()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nBye!")
        exit()

