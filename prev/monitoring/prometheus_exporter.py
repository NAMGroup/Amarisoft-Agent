from prometheus_client import start_http_server, Summary
import random
import time
from prometheus_client import Gauge



import psutil


class Metrics:
    def __init__(self,):
        #cpu relared metrics
        self.cpu_count = Gauge("host_cpu_count", "Number of CPUs on host" )
        self.cpu_usage = Gauge("host_cpu_usage", "Total CPU usage" )
        self.per_cpu_usage = list()
        #memory related metrics
        self.mem_total=Gauge("total_memory", "total host memory" )
        self.mem_available=Gauge("available_memory", "available host memory" )
        self.mem_used_percent=Gauge("used_memory_percent", "used memory" )
        self.mem_available_percent=Gauge("available_memory_percent", "available host memory" )

    def get_cpu_load(self,):
        url=self.prefix
        url+=self.user_name
        url+=":"
        url+=self.password
        url+="@"
        url+=self.ip
        return url



metrics=Metrics()





def main():
    # Start up the server to expose the metrics.
    start_http_server(22000)

    #create a list for cpus
    total_cpus=psutil.cpu_count()
    cpu_index=0
    for cpu_index in range(total_cpus):
        metrics.per_cpu_usage.append(Gauge("_".join(["host_cpu_usage",str(cpu_index)]), "_".join(["cpu usage for cpu",str(cpu_index)]) ) )

    # Generate some requests.
    while True:
        print("--->")
        #set metric for cpu count
        metrics.cpu_count.set(psutil.cpu_count())
        #set metric for total cpu_usage
        metrics.cpu_usage.set(float(psutil.cpu_percent()))

        #set metrics for  cpu_usage per cpu
        cpu_usage_per_cpu=psutil.cpu_percent(percpu=True);
        cpu_index=0;
        for cpu_index in range(total_cpus):
            metrics.per_cpu_usage[cpu_index].set(cpu_usage_per_cpu[cpu_index])
            cpu_index+=1
        
        #set memory related metrics
        mem_info=psutil.virtual_memory()._asdict()
        metrics.mem_total.set(mem_info["total"])
        metrics.mem_available.set(mem_info["available"])
        available_mem_percent=mem_info["available"]/mem_info["total"] *100
        used_mem_percent=(mem_info["total"]-mem_info["available"])/mem_info["total"] *100
        metrics.mem_used_percent.set(used_mem_percent)
        metrics.mem_available_percent .set(available_mem_percent)
        # metrics.mem_available_percent
        time.sleep(1)


if __name__ == '__main__':
    main()
