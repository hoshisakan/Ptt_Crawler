import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from module.date import DateTimeTools as DT
from module.handle_exception import HandleException
from module.reptile import RequestAnalysisData, RequestPageSource
from concurrent.futures import ThreadPoolExecutor
from instance.config import Initialization as Init
from module.log_generate import Loggings
import pandas as pd
import re
from module.generate_code import createRandomCode
import configparser


logger = Loggings()
output_dir_article_type = ''

def write_iterator_to_log(iterator):
    [logger.info(read_iterator_info) for read_iterator_info in iterator]

def write_iterator_multiple_to_log(iterator):
    for outside_index, outside in enumerate(iterator, 1):
        logger.info(f'The {outside_index} iterator')
        logger.info('------------------------------------------------------')
        for inner_index, inner_iterator in enumerate(outside, 1):
            logger.info(f"The {inner_index} data is {inner_iterator}")
        logger.info('------------------------------------------------------')

class PttInfoDownload:
    def __init__(self, article_image_info):
        self.__article_image_info = article_image_info

    def __download_article_images(self, image_info):
        logger.info(f'Downloading {image_info[0]} link image to {image_info[1]}')
        if image_info[0] and image_info[1]:
            try:
                with RequestPageSource(url=image_info[0], mode=False) as res:
                    with open(image_info[1], 'wb') as f:
                        f.write(res.content)
                        logger.info(f'Download successful from {image_info[0]}')
            except Exception as e:
                logger.error(e.args[0])
        else:
            logger.warning(f'Invalid url {image_info[0]} or save path: {image_info[1]}')

    def run(self):
        write_iterator_to_log(self.__article_image_info)
        # logger.debug(self.__article_image_info)
        with ThreadPoolExecutor() as executor:
            executor.map(self.__download_article_images, self.__article_image_info)

class PttInfoObtain:
    def __init__(self, ** crawler):
        """
            search_page_count: ptt article search page count, default search 1 page
            allow_img_download: if set True will be download ptt image to local host
            article_title_filter: filter article title ignore no need article
            article_img_type_filter: filter article image format, example: .jpg|.png
            article_img_type_filter_allow: allow enable article image format filter
        """
        self.__base_url = crawler['base_url']
        self.__allow_img_download = crawler.get('allow_img_download', False)
        self.__article_title_filter = crawler['article_title_filter']
        self.__article_img_type_filter = crawler['article_img_type_filter']
        self.__article_img_type_filter_allow = crawler['article_img_type_filter_allow']
        self.__article_type = crawler['article_type']
        self.__info_columns = ['title', 'url', 'push_count', 'author', 'date', 'search_page']

    def __check_include_match_items(self, check_string=None, pattern=None):
        return re.search(pattern, check_string)

    def __check_dir_exists(self, check_path=None):
        return os.path.exists(check_path)

    def __check_exists_and_file_count(self, check_path=None):
        if not self.__check_dir_exists(check_path):
            logger.warning(f'Starting create directory: {check_path}')
            os.makedirs(check_path)
        return self.__check_dir_exists(check_path), len(os.listdir(check_path))

    # 蒐集文章的所有圖片連結
    def __collect_images_url(self, **article):
        image_related_params_list = []
        try:
            with RequestAnalysisData(url=article['url'], mode=False, cookies={'over18': '1'}) as soup:
                all_image_a_tag = soup.find_all('a', {'href': re.compile(r'.jpg|.jpeg|.png|.gif|reurl.cc|imgur')})
                if all_image_a_tag is None or any(all_image_a_tag) is False:
                    logger.error(f"The article {article['title']} of link {article['url']} not found match image url")
                else:
                    article_title = re.sub('[\\\\/:*?"<>!|.]', '', article['title'])
                    output_path = f"{Init.output_path}\\img\\{self.__article_type}\\All\\{article['date']}\\{article_title}" if 'keyword' not in article or article['keyword'] is None or not article['keyword'] else f"{Init.output_path}/img/{self.__article_type}/{article['keyword']}/{article['date']}/{article_title}"
                    check_dir_exist, dir_file_count = self.__check_exists_and_file_count(output_path)
                    logger.debug(f'The path {output_path} is exists? {check_dir_exist}, that directory file count is: {dir_file_count}')

                    if check_dir_exist and dir_file_count == 0:
                        # 遍歷該篇文章所有的圖片連結
                        for index, one_of_image_a_tag in enumerate(all_image_a_tag, 1):
                            if one_of_image_a_tag:
                                # 若其連結副檔名有包含 「jpg,jpeg,png,gif」，則直接獲取該篇文章的圖片連結
                                one_of_image_url = one_of_image_a_tag['href']
                                filename = one_of_image_url.split('/')[-1]
                                logger.warning(f'check filename: {filename}')
                                # 若該文章中的圖片其副檔名未包含「jpg,jpeg,png,gif」，且並非是 imgur.com 該網站的圖片，則透過 selenium 開啟其圖片連結，獲取圖片真正的連結
                                if self.__check_include_match_items(check_string=filename, pattern='.jpg|.jpeg|.png|.gif') is None and one_of_image_url.find('imgur.com') == -1:
                                        with RequestPageSource(url=one_of_image_url, mode=False) as res:
                                            content = res.text.split('content=')
                                            one_of_image_url = content[1].split('>')[0].replace('"', '').strip('/')
                                            filename = one_of_image_url.split('/')[-1]
                                            logger.debug(f'Image real url is: {one_of_image_url}, filename is: {filename}')
                                # 若該文章中的圖片其副檔名未包含「jpg,jpeg,png,gif」，且是 imgur.com 該網站的圖片，則替換 imgur.com 至 i.imgur.com
                                elif self.__check_include_match_items(check_string=filename, pattern='.jpg|.jpeg|.png|.gif') is None and one_of_image_url.find('imgur.com') > 0:
                                    one_of_image_url = one_of_image_url.replace('imgur.com', 'i.imgur.com') + '.png'
                                    filename = one_of_image_url.split('/')[-1]
                                    logger.debug(f"Image real url is: {one_of_image_url}, filename is: {filename}")
                                save_path = os.path.join(output_path, filename)
                                if self.__article_img_type_filter_allow is False or self.__check_include_match_items(check_string=one_of_image_url, pattern=self.__article_img_type_filter) is None:
                                    image_related_params_list.extend([(one_of_image_url, save_path)])
                                else:
                                    logger.warning(f'The {filename} no match will be ignore.')
                    elif check_dir_exist and dir_file_count > 0:
                        logger.info(f'The {article_title} has been download image to path: {output_path}')
        except Exception as e:
            logger.error(HandleException.show_exp_detail_message(e))
        return image_related_params_list

    def ptt_scrape_by_page_count(self, search_page_count=1):
        info = []
        result = {
            'json_rows': '',
            'task_mark': ''
        }
        try:
            if self.__base_url is None:
                raise Exception('The base url is required.')
            full_url = self.__base_url
            is_last_page = False
            for current_page_count in range(0, search_page_count):
                current_page_article_image_related = []
                logger.info(f'Obtain article from the url: {full_url}')
                with RequestAnalysisData(url=full_url, mode=False, cookies={'over18': '1'}) as soup:
                    main_container_div_tag = soup.find('div', {'id': 'main-container'})
                    topbar_container_div_tag = soup.find('div', {'id': 'topbar-container'})

                    if main_container_div_tag is None:
                        raise Exception("Load main container div tag failed.")

                    article_topbar_div_tag = topbar_container_div_tag.find('div', {'id': 'topbar', 'class': 'bbs-content'})
                    article_topbar_a_tag = article_topbar_div_tag.find_all('a')[1] if article_topbar_div_tag is not None else None
                    article_type = article_topbar_a_tag.getText().strip().replace('看板 ', '') if article_topbar_a_tag is not None else 'Unknown'

                    if not result['task_mark']:
                        result['task_mark'] = article_type

                    logger.info(f"Task mark the article type is: {result['task_mark']}")

                    article_div_tag = main_container_div_tag.find('div', {'class': 'r-list-container action-bar-margin bbs-screen'})
                    all_article_div_tag = article_div_tag.find_all('div', {'class': 'r-ent'}) if article_div_tag is not None else None
                    
                    if all_article_div_tag is None:
                        raise Exception("Load all article page div tag failed.")
                    
                    action_bar_div_tag = main_container_div_tag.find('div', {'id': 'action-bar-container'})
                    go_back_div_tag = action_bar_div_tag.find('div', {'class': 'btn-group btn-group-paging'})
                    go_back_a_tag = go_back_div_tag.find_all('a', {'class': 'btn wide'}, string="‹ 上頁")
                    
                    if go_back_a_tag is None or not go_back_a_tag:
                        is_last_page = True
                    else:
                        full_url = "https://www.ptt.cc/" + go_back_a_tag[0]['href']

                    for index, one_of_article in enumerate(all_article_div_tag, 1):
                        # logger.info(f'Staring get the {index} article')
                        title_div_tag = one_of_article.find('div', {'class': 'title'})
                        title_and_link_a_tag = title_div_tag.find('a') if title_div_tag is not None else None
                        title = title_and_link_a_tag.getText().strip() if title_and_link_a_tag is not None else ''
            
                        if title and self.__check_include_match_items(check_string=title, pattern=self.__article_title_filter) is None:
                            # logger.info(f'Obtain article title is: {title}')
                            link = "https://www.ptt.cc" + title_and_link_a_tag['href'] if title_and_link_a_tag is not None else ''
                            push_count_div_tag = one_of_article.find('div', {'nrec'})
                            
                            if push_count_div_tag is not None:
                                push_count = str(push_count_div_tag.get_text().strip())
                                if push_count and push_count.isdigit() is True:
                                    push_count = int(push_count)
                                elif push_count and push_count.isdigit() is False and push_count.find('爆') != -1:
                                    push_count = 100
                                elif push_count and push_count.isdigit() is False and push_count.find('X') != -1:
                                    push_count = -1
                                else:
                                    push_count = 0
                            
                            author_date_div_tag = one_of_article.find('div', {'class': 'meta'})
                            if author_date_div_tag is not None:
                                author_div_tag = author_date_div_tag.find('div', {'class': 'author'})
                                author = author_div_tag.getText().strip() if author_div_tag is not None else ''
                                date_div_tag = author_date_div_tag.find('div', {'class': 'date'})
                                date = date_div_tag.get_text().strip() if date_div_tag is not None else ''
                            
                            if date:
                                try:
                                    date_split = date.split('/')
                                    month = int(date_split[0])
                                    day = int(date_split[1])
                                    if day > 0 and day < 10:
                                        day = f'0{day}'
                                    if month > 0 and month < 10:
                                        date = f'0{month}-{day}'
                                    else:
                                        date = f'{month}-{day}'
                                except ValueError:
                                    logger.error(f'Obtain date of month failed: {date}')
                                else:
                                    temp_one_of_article = [title, link, push_count, author, date, current_page_count + 1]
                                    # logger.debug(temp_one_of_article)
                                    info.append(dict(zip(self.__info_columns, temp_one_of_article)))
                                    if self.__allow_img_download is True:
                                        current_page_article_image_related.extend(
                                            self.__collect_images_url(
                                            title=title,
                                            url=link,
                                            date=date,
                                            keyword=None))
                if self.__allow_img_download is True and any(current_page_article_image_related) is True:
                    downloader = PttInfoDownload(current_page_article_image_related)
                    downloader.run()
                current_page_article_image_related.clear()
                if is_last_page is True:
                    break
            # info = sorted(info, key=lambda x: x['date'], reverse=True)
            info = sorted(info, key=lambda x: x['search_page'], reverse=False)
            result['json_rows'] = info
            # write_iterator_to_log(result['task_mark'])
        except Exception as e:
            logger.error(HandleException.show_exp_detail_message(e))
        return result

    def ptt_scrape_by_keyword(self, keyword=None, search_page_limit=1, page_search_over_limit=False):
        info = []
        result = {
            'json_rows': '',
            'task_mark': ''
        }
        try:
            if self.__base_url is None:
                raise Exception('The base url is required.')
            full_url = self.__base_url if keyword is None or not keyword else self.__base_url.replace('/index.html', '') + f'/search?q={keyword}'
            current_page_count = 0
            is_last_page = False
            while True:
                current_page_article_image_related = []
                current_page_article_title = []
                logger.info(f'Obtain article from the url: {full_url}')
                with RequestAnalysisData(url=full_url, mode=False, cookies={'over18': '1'}) as soup:
                    main_container_div_tag = soup.find('div', {'id': 'main-container'})
                    topbar_container_div_tag = soup.find('div', {'id': 'topbar-container'})

                    if main_container_div_tag is None:
                        raise Exception("Load main container div tag failed.")

                    article_topbar_div_tag = topbar_container_div_tag.find('div', {'id': 'topbar', 'class': 'bbs-content'})
                    article_topbar_a_tag = article_topbar_div_tag.find_all('a')[1] if article_topbar_div_tag is not None else None
                    article_type = article_topbar_a_tag.getText().strip().replace('看板 ', '') if article_topbar_a_tag is not None else 'Unknown'

                    if not result['task_mark']:
                        result['task_mark'] = article_type

                    logger.info(f"Task mark the article type is: {result['task_mark']}")

                    article_div_tag = main_container_div_tag.find('div', {'class': 'r-list-container action-bar-margin bbs-screen'})
                    all_article_div_tag = article_div_tag.find_all('div', {'class': 'r-ent'}) if article_div_tag is not None else None
                    
                    if all_article_div_tag is None:
                        raise Exception("Load all article page div tag failed.")
                    
                    action_bar_div_tag = main_container_div_tag.find('div', {'id': 'action-bar-container'})
                    go_back_div_tag = action_bar_div_tag.find('div', {'class': 'btn-group btn-group-paging'})
                    go_back_a_tag = go_back_div_tag.find_all('a', {'class': 'btn wide'}, string="‹ 上頁")
                    
                    if go_back_a_tag is None or not go_back_a_tag:
                        is_last_page = True
                    else:
                        full_url = "https://www.ptt.cc/" + go_back_a_tag[0]['href']

                    logger.info(f'Go back article link is: {full_url}')

                    for index, one_of_article in enumerate(all_article_div_tag, 1):
                        # logger.info(f'Staring get the {index} article')
                        title_div_tag = one_of_article.find('div', {'class': 'title'})
                        title_and_link_a_tag = title_div_tag.find('a') if title_div_tag is not None else None
                        title = title_and_link_a_tag.getText().strip().replace(u'\u3000', u'') if title_and_link_a_tag is not None else ''
            
                        if title and self.__check_include_match_items(check_string=title, pattern=self.__article_title_filter) is None:
                            # logger.info(f'Obtain article title is: {title}')
                            link = "https://www.ptt.cc" + title_and_link_a_tag['href'] if title_and_link_a_tag is not None else ''
                            push_count_div_tag = one_of_article.find('div', {'nrec'})
                            
                            if push_count_div_tag is not None:
                                push_count = str(push_count_div_tag.get_text().strip())
                                if push_count and push_count.isdigit() is True:
                                    push_count = int(push_count)
                                elif push_count and push_count.isdigit() is False and push_count.find('爆') != -1:
                                    push_count = 100
                                elif push_count and push_count.isdigit() is False and push_count.find('X') != -1:
                                    push_count = -1
                                else:
                                    push_count = 0
                            
                            author_date_div_tag = one_of_article.find('div', {'class': 'meta'})
                            if author_date_div_tag is not None:
                                author_div_tag = author_date_div_tag.find('div', {'class': 'author'})
                                author = author_div_tag.getText().strip() if author_div_tag is not None else ''
                                date_div_tag = author_date_div_tag.find('div', {'class': 'date'})
                                date = date_div_tag.get_text().strip() if date_div_tag is not None else ''
                            
                            if date:
                                try:
                                    date_split = date.split('/')
                                    month = int(date_split[0])
                                    day = int(date_split[1])
                                    if day > 0 and day < 10:
                                        day = f'0{day}'
                                    if month > 0 and month < 10:
                                        date = f'0{month}-{day}'
                                    else:
                                        date = f'{month}-{day}'
                                except ValueError:
                                    logger.error(f'Obtain date of month failed: {date}')
                                else:
                                    current_page_article_title.append(title)
                                    temp_one_of_article = [title, link, push_count, author, date, current_page_count + 1]
                                    # logger.debug(temp_one_of_article)
                                    info.append(dict(zip(self.__info_columns, temp_one_of_article)))
                                    if self.__allow_img_download is True:
                                        current_page_article_image_related.extend(
                                            self.__collect_images_url(
                                            title=title,
                                            url=link,
                                            date=date,
                                            keyword=keyword))
                if self.__allow_img_download is True and any(current_page_article_image_related) is True:
                    downloader = PttInfoDownload(current_page_article_image_related)
                    downloader.run()
                # logger.warning(current_page_article_title)
                current_page_count += 1
                if page_search_over_limit is False and current_page_count == search_page_limit or is_last_page is True or any([True for one_of_title in current_page_article_title if one_of_title.find(keyword) != -1]) is False:
                    logger.info(f'Not found keyword {keyword} info or page has been last page.')
                    current_page_article_image_related.clear()
                    current_page_article_title.clear()
                    break
                current_page_article_image_related.clear()
                current_page_article_title.clear()
            # info = sorted(info, key=lambda x: x['date'], reverse=True)
            info = sorted(info, key=lambda x: x['search_page'], reverse=False)
            result['json_rows'] = info
            # write_iterator_to_log(result['task_mark'])
        except Exception as e:
            logger.error(HandleException.show_exp_detail_message(e))
        return result

    def ptt_scrape_by_date(self, target_date=None):
        info = []
        result = {
            'json_rows': '',
            'task_mark': ''
        }
        try:
            if self.__base_url is None:
                raise Exception('The base url is required.')
            full_url = self.__base_url
            current_page_count = 0
            found_target_mark = False
            found_target_date_count = 0
            keep_search = False
            is_last_page = False

            while True:
                logger.debug(f'Starting {current_page_count + 1} page search')
                current_page_article_date = []
                # current_page_article_target_date = []
                current_page_article_image_related = []

                logger.info(f'Obtain article from the url: {full_url}')
                with RequestAnalysisData(url=full_url, mode=False, cookies={'over18': '1'}) as soup:
                    main_container_div_tag = soup.find('div', {'id': 'main-container'})
                    topbar_container_div_tag = soup.find('div', {'id': 'topbar-container'})

                    if main_container_div_tag is None:
                        raise Exception("Load main container div tag failed.")

                    article_topbar_div_tag = topbar_container_div_tag.find('div', {'id': 'topbar', 'class': 'bbs-content'})
                    article_topbar_a_tag = article_topbar_div_tag.find_all('a')[1] if article_topbar_div_tag is not None else None
                    article_type = article_topbar_a_tag.getText().strip().replace('看板 ', '') if article_topbar_a_tag is not None else 'Unknown'

                    if not result['task_mark']:
                        result['task_mark'] = article_type

                    logger.info(f"Task mark the article type is: {result['task_mark']}")

                    article_div_tag = main_container_div_tag.find('div', {'class': 'r-list-container action-bar-margin bbs-screen'})
                    all_article_div_tag = article_div_tag.find_all('div', {'class': 'r-ent'}) if article_div_tag is not None else None
                    
                    if all_article_div_tag is None:
                        raise Exception("Load all article page div tag failed.")
                    
                    action_bar_div_tag = main_container_div_tag.find('div', {'id': 'action-bar-container'})
                    go_back_div_tag = action_bar_div_tag.find('div', {'class': 'btn-group btn-group-paging'})
                    go_back_a_tag = go_back_div_tag.find_all('a', {'class': 'btn wide'}, string="‹ 上頁")
                    
                    if go_back_a_tag is None or not go_back_a_tag:
                        is_last_page = True
                    else:
                        full_url = "https://www.ptt.cc/" + go_back_a_tag[0]['href']

                    for index, one_of_article in enumerate(all_article_div_tag, 1):
                        # logger.info(f'Staring get the {index} article')
                        title_div_tag = one_of_article.find('div', {'class': 'title'})
                        title_and_link_a_tag = title_div_tag.find('a') if title_div_tag is not None else None
                        title = title_and_link_a_tag.getText().strip() if title_and_link_a_tag is not None else ''
            
                        if title and self.__check_include_match_items(check_string=title, pattern=self.__article_title_filter) is None:
                            # logger.info(f'Obtain article title is: {title}')
                            link = "https://www.ptt.cc" + title_and_link_a_tag['href'] if title_and_link_a_tag is not None else ''
                            push_count_div_tag = one_of_article.find('div', {'nrec'})
                            
                            if push_count_div_tag is not None:
                                push_count = str(push_count_div_tag.get_text().strip())
                                if push_count and push_count.isdigit() is True:
                                    push_count = int(push_count)
                                elif push_count and push_count.isdigit() is False and push_count.find('爆') != -1:
                                    push_count = 99
                                elif push_count and push_count.isdigit() is False and push_count.find('X') != -1:
                                    push_count = -1
                                else:
                                    push_count = 0
                            
                            author_date_div_tag = one_of_article.find('div', {'class': 'meta'})
                            if author_date_div_tag is not None:
                                author_div_tag = author_date_div_tag.find('div', {'class': 'author'})
                                author = author_div_tag.getText().strip() if author_div_tag is not None else ''
                                date_div_tag = author_date_div_tag.find('div', {'class': 'date'})
                                date = date_div_tag.get_text().strip() if date_div_tag is not None else ''
                            
                            if date:
                                try:
                                    date_split = date.split('/')
                                    month = int(date_split[0])
                                    day = int(date_split[1])
                                    if day > 0 and day < 10:
                                        day = f'0{day}'
                                    if month > 0 and month < 10:
                                        date = f'0{month}-{day}'
                                    else:
                                        date = f'{month}-{day}'
                                except ValueError:
                                    logger.error(f'Obtain date of month failed: {date}')
                                else:
                                    current_page_article_date.append(date)
                                    if target_date is not None and target_date == date:
                                        # found_target_date_count += 1
                                        temp_one_of_article = [title, link, push_count, author, date, current_page_count + 1]
                                        # logger.debug(temp_one_of_article)
                                        info.append(dict(zip(self.__info_columns, temp_one_of_article)))
                                        if self.__allow_img_download is True:
                                            current_page_article_image_related.extend(
                                                self.__collect_images_url(
                                                title=title,
                                                url=link,
                                                date=date))
                                    else:
                                        logger.warning(f'The article date {date} does not match with target date {target_date}')
                if self.__allow_img_download is True and any(current_page_article_image_related) is True:
                    downloader = PttInfoDownload(current_page_article_image_related)
                    downloader.run()
                logger.debug(current_page_article_date)
                found_target_date_count = current_page_article_date.count(target_date)

                if found_target_date_count > 0:
                    found_target_mark = True
                    keep_search = True
                else:
                    keep_search = False

                logger.debug(f'found date count: {found_target_date_count}\nfound target mark:{found_target_mark}\nkeep search?{keep_search}')

                if is_last_page is True or current_page_count > 0 and found_target_mark is True and keep_search is False:
                    current_page_article_date.clear()
                    current_page_article_image_related.clear()
                    break

                # logger.warning(f'{current_page_article_date.count(target_date)}')
                current_page_article_date.clear()
                current_page_article_image_related.clear()
                # found_target_date_count = 0
                current_page_count += 1
            # info = sorted(info, key=lambda x: x['date'], reverse=True)
            info = sorted(info, key=lambda x: x['search_page'], reverse=False)
            result['json_rows'] = info
                # write_iterator_to_log(result['task_mark'])
        except Exception as e:
            logger.error(HandleException.show_exp_detail_message(e))
        return result

def timer(func):
    def time_count():
        exc_start_time = DT.get_current_datetime()
        func()
        exc_end_time = DT.get_current_datetime()
        exc_time = exc_end_time - exc_start_time
        msg = "執行時間: {}".format(exc_time)
        logger.info(msg)
    return time_count

def init_global():
    config = configparser.ConfigParser()
    logger.debug(Init.setting_file_path)
    config.read(Init.setting_file_path, encoding="utf-8")
    Init.output_path = config.get("Settings", "Output_Path", fallback="./Output/ptt")
    Init.base_url = config.get("Settings", "Base_URL", fallback="https://www.ptt.cc/bbs/Baseball/index.html")
    Init.article_search_keyword = config.get("Settings", "Article_Search_Keyword", fallback="測試")
    Init.article_search_page_limit = int(config.get("Settings", "Article_Search_Page_Limit", fallback="1"))
    temp_page_search_over_limit = config.get("Settings", "Page_Search_Over_Limit", fallback='NO')
    Init.page_search_over_limit = False if not temp_page_search_over_limit or temp_page_search_over_limit.upper() == 'NO' else True
    Init.article_target_date = config.get("Settings", "Article_Target_Date", fallback=DT.get_date_no_year())
    temp_allow_image_download = config.get("Settings", "Allow_Imgage_Download", fallback='NO')
    Init.allow_img_download = False if not temp_allow_image_download or temp_allow_image_download.upper() == 'NO' else True
    Init.action_mode_by = config.get("Settings", "Action_Mode_By", fallback="Page")
    Init.article_title_filter = config.get("Settings", "Article_Title_Filter", fallback="帥哥|公告|大尺碼|肉特|選情報導|整理")
    Init.article_img_type_filter = config.get("Settings", "Article_Img_Type_Filter", fallback=".gif")
    temp_article_img_type_filter_allow = config.get("Settings", "Article_Img_Type_Filter_Allow", fallback='YES')
    Init.article_img_type_filter_allow = False if not temp_article_img_type_filter_allow or temp_article_img_type_filter_allow.upper() == 'NO' else True

def run_job():
    result = []

    init_global()

    article_type = Init.base_url.split('/')[4] if Init.base_url else 'Unknown'

    crawler = PttInfoObtain(
        base_url=Init.base_url,
        allow_img_download=Init.allow_img_download,
        article_title_filter=Init.article_title_filter,
        article_img_type_filter=Init.article_img_type_filter,
        article_img_type_filter_allow=Init.article_img_type_filter_allow,
        article_type=article_type
    )

    if Init.action_mode_by == 'Date' or Init.action_mode_by == 'date':
        logger.debug(f'Crawler targert url is: {Init.base_url}\ntarget date is: {Init.article_target_date}')
        result = crawler.ptt_scrape_by_date(Init.article_target_date)
    elif Init.action_mode_by == 'Keyword' or Init.action_mode_by == 'keyword':
        logger.debug(f'Crawler targert url is: {Init.base_url}\nkeyword is: {Init.article_search_keyword}\nsearch page limit is: {Init.article_search_page_limit}\nover search page limit is: {Init.page_search_over_limit}')
        result = crawler.ptt_scrape_by_keyword(
            keyword=Init.article_search_keyword,
            search_page_limit=Init.article_search_page_limit,
            page_search_over_limit=Init.page_search_over_limit
        )
    elif Init.action_mode_by == 'Page' or Init.action_mode_by == 'page':
        logger.debug(f'Crawler targert url is: {Init.base_url}\nsearch page limit is: {Init.article_search_page_limit}')
        result = crawler.ptt_scrape_by_page_count(Init.article_search_page_limit)

    if 'json_rows' in result and result['json_rows']:
        # write_iterator_to_log(result['json_rows'])
        logger.info(result['task_mark'])
        dataframe = pd.DataFrame(result['json_rows'])
        logger.debug(dataframe)
        logger.info(f"Article total is: {len(result['json_rows'])}")
        output_path = f'{Init.output_path}\\csv\\{article_type}'
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        dataframe.to_csv(
            f"{output_path}\\{DT.get_date('_')}_{createRandomCode()}.csv",
            encoding='utf-8-sig',index=False)
    else:
        logger.error('Task execute failed.')


@timer
def main():
    run_job()

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logger.error(HandleException.show_exp_detail_message(e))
    except KeyboardInterrupt:
        os._exit(0)