#!/bin/bash
echo "启动论文AI检测系统..."
mkdir -p data/uploads data/results
docker-compose up -d
echo "等待服务启动..."
sleep 10
docker-compose exec backend python -c "from app.database import init_db; init_db()"
echo "系统启动完成！"
echo "前端地址: http://localhost:3000"
echo "后端API: http://localhost:8000/docs"
