import re

from ..items import ExtensionItem


class ParserDispatch:
    @staticmethod
    def parse_ext(json_date):
        ext = ExtensionItem()
        ext['code_id'] = json_date[0][1][1][0][0]
        ext['name'] = json_date[0][1][1][0][1]
        ext['short_intro'] = json_date[0][1][1][0][6]
        ext['rank'] = json_date[0][1][1][0][12]
        ext['download_count'] = re.sub(r',|\+', r'', json_date[0][1][1][0][23])
        # 有点需要注意的地方
        ext['provider'] = json_date[0][1][1][0][35]
        if not ext['provider']:
            ext['provider'] = json_date[0][1][1][0][2]
        m = re.search(r'(^免费$)|(^free$)', json_date[0][1][1][0][30], re.I)
        if m:
            ext['free'] = 1
        else:
            ext['free'] = 0
        ext['update_time'] = json_date[0][1][1][7]
        ext['image_urls'] = []
        # 缩略图
        ext['image_urls'].append(json_date[0][1][1][0][3])
        for img in json_date[0][1][1][11]:
            # 介绍图
            if img[17]:
                ext['image_urls'].append(img[17])
            # 视频，下载后无法播放
            # if img[19]:
            #     ext['file_urls'].append(img[19])
        return ext

    @staticmethod
    def parse_detail_info(json_date):
        detail_introduce = json_date[0][1][1][1]
        # 被这个坑了几个小时！
        detail_introduce = re.sub(r"\n", r"\\n", detail_introduce)
        version = json_date[0][1][1][6]
        website = json_date[0][1][1][3]
        size = json_date[0][1][1][25]
        language = json_date[0][1][1][8]
        # 可能不存在，存在是选[35][2]，所以很不方便
        developer_list = json_date[0][1][1][35]
        if developer_list:
            det = 3 - len(developer_list)
            for _ in range(det):
                developer_list.append(None)
        else:
            developer_list = [None, None, None]
        developer_email = developer_list[0]
        developer_addr = developer_list[1]
        privacy_policy = developer_list[2]

        type_name = json_date[0][1][1][0][10]
        return {
            'detail_introduce': detail_introduce,
            'version': version,
            'website': website,
            'size': size,
            'language': language,
            'developer_email': developer_email,
            'developer_addr': developer_addr,
            'privacy_policy': privacy_policy,
            'type_name': type_name,
        }

    @staticmethod
    def parse_related_ext(json_date):
        rel_exts = []
        for i in range(2, 4):
            for j in range(len(json_date[0][1][i])):
                name = json_date[0][1][i][j][1]
                rank = json_date[0][1][i][j][12]
                download_num = re.sub(',', '', json_date[0][1][i][j][23])
                code_id = json_date[0][1][i][j][0]
                rel_exts.append({
                    'name': name,
                    'rank': rank,
                    'download_num': download_num,
                    'code_id': code_id,
                })
        return rel_exts