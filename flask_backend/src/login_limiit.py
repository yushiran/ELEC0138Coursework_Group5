from datetime import datetime, timedelta
from pymongo.mongo_client import MongoClient

def update_login_attempts(username, login_attempts_db ,success=False):
    """
    更新用户的登录尝试记录
    :param username: 用户名
    :param success: 登录是否成功
    """
    if success:
        # 登录成功，重置失败计数
        login_attempts_db.update_one(
            {'username': username},
            {'$set': {'failed_attempts': 0, 'locked_until': None}},
            upsert=True
        )
    else:
        # 登录失败，增加失败计数
        attempt_record = login_attempts_db.find_one({'username': username})
        if not attempt_record:
            # 第一次失败
            login_attempts_db.insert_one({
                'username': username,
                'failed_attempts': 1,
                'locked_until': None,
                'last_attempt': datetime.utcnow()
            })
        else:
            # 累计失败次数
            failed_attempts = attempt_record.get('failed_attempts', 0) + 1
            locked_until = None
            
            # 如果失败次数达到3次，锁定账户10分钟
            if failed_attempts >= 3:
                locked_until = datetime.utcnow() + timedelta(minutes=10)
                
            login_attempts_db.update_one(
                {'username': username},
                {
                    '$set': {
                        'failed_attempts': failed_attempts,
                        'locked_until': locked_until,
                        'last_attempt': datetime.utcnow()
                    }
                }
            )