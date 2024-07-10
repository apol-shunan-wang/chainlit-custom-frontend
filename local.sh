# docker-compose と docker compose の２つのバージョンがあるので
docker_compose="docker-compose"
chk=$(which ${docker_compose})
if [ "$chk" = "" ]; then
  docker_compose="docker compose"
fi

# 設定
COMPOSE_FILE="docker-compose.local.yml"

# -e エラー発生時に終了させる
set -e

help(){
  echo ""
  echo "sh $0 <command>"
  echo ""
  echo "  restart             down & up"
  echo "  down                down"
  echo "  up                  up"
  echo "  logneo4j            logs -f neo4j"
  echo "  logchainlit         logs -f chainlit"
  echo "  build               neo4j: requiremets.txt を変更したときに実行"
  echo "  ps                  ps -a"
  echo "  docker-rmi-dangling          tag がついていない docker images を削除"
  echo "  docker-rmi-check <pattern>   pattern を含む docker images を表示"
  echo "  docker-rmi-do <pattern>      pattern を含む docker images を削除"
  echo ""
}

command=$1
if [ -z "${command}" ]; then
  help
  exit 1
fi
shift

case ${command} in
  restart)
    ${docker_compose} -f ${COMPOSE_FILE} down;
    echo "docker restart"
    ${docker_compose} -f ${COMPOSE_FILE} up -d;
    ${docker_compose} -f ${COMPOSE_FILE} exec neo4j /var/lib/neo4j/bin/cypher-shell -u neo4j -p mocmocmoc -d neo4j -f /testdata/init_data;
    ;;
  down)
    ${docker_compose} -f ${COMPOSE_FILE} down;
    ;;
  up)
    echo "docker start data"
    ${docker_compose} -f ${COMPOSE_FILE} up -d;
    ${docker_compose} -f ${COMPOSE_FILE} exec neo4j /var/lib/neo4j/bin/cypher-shell -u neo4j -p mocmocmoc -d neo4j -f /testdata/init_data;
    ;;
  logneo4j)
    ${docker_compose} -f ${COMPOSE_FILE} logs -f neo4j;
    ;;
  logchainlit)
    ${docker_compose} -f ${COMPOSE_FILE} logs -f chainlit;
    ;;
  build)
    ${docker_compose} -f ${COMPOSE_FILE} build;
    ;;
  ps)
    ${docker_compose} -f ${COMPOSE_FILE} ps -a;
    ;;
  docker-rmi-dangling)
    docker rmi $(docker images -f "dangling=true" -q)
    ;;
  docker-rmi-check)
    arg=${1:-none}
    echo "docker images -a | grep ${arg}"
    docker images -a | grep ${arg}
    ;;
  docker-rmi-do)
    arg=${1:-none}
    docker images -a | grep ${arg} | awk '{print $3}' | xargs docker rmi
    ;;
  *)
    help
    exit 1
    ;;
esac
