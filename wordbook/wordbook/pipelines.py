# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import xlwt
# 写入excel


class WordbookPipeline(object):
    book_dict = locals()
    book_name_set = set()

    def process_item(self, item, spider):
        book_name = item[0]  # get the book name
        if book_name not in self.book_name_set:
            self.book_name_set.add(book_name)
            self.book_dict['%s' % book_name] = xlwt.Workbook(encoding='utf-8')

        row = 0
        unit = 'unit' + str(item[1])   # get the unit name
        # print(self.unit,unit)
        sheet = self.book_dict[book_name].add_sheet(unit)
        for i in range(len(item[2]['word'])):
            sheet.write(row, 0, item[2]['word'][i])
            sheet.write(row, 1, item[2]['meaning'][i])
            row += 1

        self.book_dict[book_name].save('{}.xls'.format(book_name))
        return item

    # def close_spider(self, spider):
    #     for book in self.book_name_set:
    #         # print("closing ", book)
    #         self.book_dict[book].save('{}.xls'.format(book))