#### 使用方法

##### 1、运行python main.py

##### 2、本地调用/login_by_ldap，输入个人账号form表单，获取个人拥有项目组（group_name:group_id）

##### 3、本地调用/get_groups/<group_id>，获取单个组下的所有项目（project_name:project_id）

##### 4、本地调用/get_project_token/<project_id>，获取单个项目下的所有接口分类（接口分类名:接口分类ID）

##### 5、本地调用/encapsulation_by_catalog/<project_id>/<接口分类ID>，生成rpc接口封装的格式
