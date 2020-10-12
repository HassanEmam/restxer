# @api.expect(schedule)
# def post(self):
#     p = os.path.abspath('.')
#     p = os.path.join(p, 'programmes')
#     args = self.schedule.parse_args()
#     uploaded_file = args['file']
#     extension = uploaded_file.filename.split('.')[-1]
#     filename = uploaded_file.filename.replace('.' + extension, '')
#     print(filename, extension)
#     xerfile = os.path.join(p, uploaded_file.filename)
#     uploaded_file.save(xerfile)
#     return self.importer(xerfile)
#
# def importer(self, filename):
#     dic = defaultdict(dict)
#     file = Reader(filename)
#     for p in file.projects:
#         for wbs in p.wbss:
#             if dic[p.proj_id].get('wbs'):
#                 dic[p.proj_id]['wbs'][str(wbs.wbs_id)] = {'name': wbs.wbs_name}
#             else:
#                 dic[p.proj_id]['wbs'] = {}
#                 dic[p.proj_id]['wbs'][str(wbs.wbs_id)] = {'name': wbs.wbs_name}
#             for a in wbs.activities:
#                 if dic[p.proj_id]['wbs'][str(wbs.wbs_id)].get('activities'):
#                     dic[p.proj_id]['wbs'][str(wbs.wbs_id)]['activities'] \
#                         [a.task_id] = {'id': a.task_code, 'start': str(a.early_start_date),
#                                        'end': str(a.early_end_date)}
#                 else:
#                     dic[p.proj_id]['wbs'][str(wbs.wbs_id)]['activities'] = {}
#                     dic[p.proj_id]['wbs'][str(wbs.wbs_id)]['activities'] \
#                         [a.task_id] = {'id': a.task_code, 'start': str(a.early_start_date),
#                                        'end': str(a.early_end_date)}
#     return dic

# def get(self):
#     pass