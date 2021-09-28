import os

class Initialization:
    base_url = 'https://www.ptt.cc/bbs/Baseball/index.html'
    output_path = "D:\Files\Project\Ptt\output"
    setting_file_path = os.path.join(os.getcwd(), 'crawler.ini')
    action_mode_by = 'Page'
    article_search_page_limit = 5
    article_search_keyword = '測試'
    article_title_filter = '帥哥|公告|大尺碼|肉特|選情報導|整理'
    article_img_type_filter = '.jpg|.jpeg|.png|.gif'
    allow_img_download = 'NO'
    article_target_date='09-27'