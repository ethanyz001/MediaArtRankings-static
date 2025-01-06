from django.shortcuts import render

# 主页面
def ranking_page(request):
    return render(request, 'rankings/index.html')

# 相关会议页面
def related_conferences_view(request):
    return render(request, 'rankings/related_conferences.html')

# READ ME 页面
def read_me_view(request):
    return render(request, 'rankings/read_me.html')
